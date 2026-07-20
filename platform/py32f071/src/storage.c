#include "py32f071_board.h"
#include "py32f071_regs.h"

#include <string.h>

#define STORAGE_MAGIC 0x46535059u /* FSPY */
#define STORAGE_VERSION 1u
#define FLASH_PAGE_SIZE 1024u
#define STORAGE_SLOT0_ADDRESS 0x0801F800u
#define STORAGE_SLOT1_ADDRESS 0x0801FC00u

#define FLASH_KEY1 0x45670123u
#define FLASH_KEY2 0xCDEF89ABu
#define FLASH_SR_BSY PY32_BIT(0)
#define FLASH_SR_EOP PY32_BIT(5)
#define FLASH_CR_PG PY32_BIT(0)
#define FLASH_CR_PER PY32_BIT(1)
#define FLASH_CR_STRT PY32_BIT(6)
#define FLASH_CR_LOCK PY32_BIT(7)

_Static_assert((sizeof(py32_stored_configuration_t) % sizeof(uint32_t)) == 0u,
               "stored configuration must be word aligned");
_Static_assert((STORAGE_SLOT0_ADDRESS % FLASH_PAGE_SIZE) == 0u,
               "slot 0 must start on a flash page");
_Static_assert((STORAGE_SLOT1_ADDRESS % FLASH_PAGE_SIZE) == 0u,
               "slot 1 must start on a flash page");

uint32_t py32_crc32(const void *data, size_t length)
{
    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < length; ++i) {
        crc ^= bytes[i];
        for (uint32_t bit = 0; bit < 8u; ++bit) {
            uint32_t mask = 0u - (crc & 1u);
            crc = (crc >> 1u) ^ (0xEDB88320u & mask);
        }
    }
    return ~crc;
}

static bool record_valid(const py32_stored_configuration_t *record)
{
    if (record->magic != STORAGE_MAGIC ||
        record->version != STORAGE_VERSION ||
        record->length != sizeof(*record)) {
        return false;
    }
    uint32_t expected = py32_crc32(record, offsetof(py32_stored_configuration_t, crc32));
    return expected == record->crc32;
}

static void flash_wait(void)
{
    while ((PY32_FLASH->SR & FLASH_SR_BSY) != 0u) {
    }
}

static void flash_unlock(void)
{
    if ((PY32_FLASH->CR & FLASH_CR_LOCK) != 0u) {
        PY32_FLASH->KEYR = FLASH_KEY1;
        PY32_FLASH->KEYR = FLASH_KEY2;
    }
}

static void flash_lock(void)
{
    PY32_FLASH->CR |= FLASH_CR_LOCK;
}

static bool flash_erase_page(uint32_t address)
{
    flash_wait();
    PY32_FLASH->SR = FLASH_SR_EOP;
    PY32_FLASH->CR = (PY32_FLASH->CR & ~FLASH_CR_PG) | FLASH_CR_PER;
    *(volatile uint32_t *)(uintptr_t)address = 0xFFFFFFFFu;
    PY32_FLASH->CR |= FLASH_CR_STRT;
    flash_wait();
    PY32_FLASH->CR &= ~FLASH_CR_PER;
    return *(volatile const uint32_t *)(uintptr_t)address == 0xFFFFFFFFu;
}

static bool flash_program_word(uint32_t address, uint32_t value)
{
    if ((address & 3u) != 0u) {
        return false;
    }

    flash_wait();
    PY32_FLASH->CR |= FLASH_CR_PG;
    *(volatile uint32_t *)(uintptr_t)address = value;
    flash_wait();
    PY32_FLASH->CR &= ~FLASH_CR_PG;
    return *(volatile const uint32_t *)(uintptr_t)address == value;
}

static bool flash_write_record(uint32_t address, const py32_stored_configuration_t *record)
{
    const uint32_t *words = (const uint32_t *)(const void *)record;
    const size_t word_count = sizeof(*record) / sizeof(uint32_t);

    flash_unlock();
    bool ok = flash_erase_page(address);
    for (size_t i = 0; ok && i < word_count; ++i) {
        ok = flash_program_word(address + (uint32_t)(i * sizeof(uint32_t)), words[i]);
    }
    flash_lock();
    return ok && record_valid((const py32_stored_configuration_t *)(uintptr_t)address);
}

bool py32_storage_load(py32_stored_configuration_t *configuration)
{
    const py32_stored_configuration_t *slot0 =
        (const py32_stored_configuration_t *)(uintptr_t)STORAGE_SLOT0_ADDRESS;
    const py32_stored_configuration_t *slot1 =
        (const py32_stored_configuration_t *)(uintptr_t)STORAGE_SLOT1_ADDRESS;
    bool valid0 = record_valid(slot0);
    bool valid1 = record_valid(slot1);

    if (!valid0 && !valid1) {
        return false;
    }

    const py32_stored_configuration_t *selected;
    if (valid0 && valid1) {
        selected = (int32_t)(slot1->sequence - slot0->sequence) > 0 ? slot1 : slot0;
    } else {
        selected = valid1 ? slot1 : slot0;
    }
    memcpy(configuration, selected, sizeof(*configuration));
    return true;
}

bool py32_storage_save(const py32_stored_configuration_t *configuration)
{
    py32_stored_configuration_t record = *configuration;
    py32_stored_configuration_t current;
    uint32_t next_sequence = py32_storage_load(&current) ? current.sequence + 1u : 1u;

    record.magic = STORAGE_MAGIC;
    record.version = STORAGE_VERSION;
    record.length = sizeof(record);
    record.sequence = next_sequence;
    record.crc32 = py32_crc32(&record, offsetof(py32_stored_configuration_t, crc32));

    uint32_t target = (next_sequence & 1u) != 0u ? STORAGE_SLOT0_ADDRESS : STORAGE_SLOT1_ADDRESS;
    return flash_write_record(target, &record);
}
