#include "py32f071_board.h"

#define USB_RX_CAPACITY 2048u
#define USB_TX_CAPACITY 2048u

static volatile uint16_t rx_head;
static volatile uint16_t rx_tail;
static volatile uint16_t tx_head;
static volatile uint16_t tx_tail;
static uint8_t rx_buffer[USB_RX_CAPACITY];
static uint8_t tx_buffer[USB_TX_CAPACITY];

#define COMPILER_MEMORY_BARRIER() __asm volatile("" ::: "memory")

/* Official Puya CherryUSB glue overrides these low-level hooks. */
__attribute__((weak)) void py32_usb_ll_init(void) {}
__attribute__((weak)) void py32_usb_ll_task(void) {}
__attribute__((weak)) bool py32_usb_ll_can_transmit(void) { return false; }
__attribute__((weak)) size_t py32_usb_ll_transmit(const uint8_t *data, size_t length)
{
    (void)data;
    (void)length;
    return 0u;
}

static uint16_t ring_next(uint16_t value, uint16_t capacity)
{
    ++value;
    return value == capacity ? 0u : value;
}

void py32_usb_init(void)
{
    rx_head = rx_tail = 0u;
    tx_head = tx_tail = 0u;
    py32_usb_ll_init();
}

void py32_usb_rx_bytes(const uint8_t *data, size_t length)
{
    for (size_t i = 0; i < length; ++i) {
        uint16_t next = ring_next(rx_head, USB_RX_CAPACITY);
        if (next == rx_tail) {
            break;
        }
        rx_buffer[rx_head] = data[i];
        COMPILER_MEMORY_BARRIER();
        rx_head = next;
    }
}

size_t py32_usb_tx_read(uint8_t *data, size_t capacity)
{
    size_t count = 0u;
    while (count < capacity && tx_tail != tx_head) {
        data[count++] = tx_buffer[tx_tail];
        COMPILER_MEMORY_BARRIER();
        tx_tail = ring_next(tx_tail, USB_TX_CAPACITY);
    }
    return count;
}

void py32_usb_task(void)
{
    py32_usb_ll_task();
    if (tx_tail != tx_head && py32_usb_ll_can_transmit()) {
        uint8_t packet[64];
        size_t count = py32_usb_tx_read(packet, sizeof(packet));
        size_t sent = py32_usb_ll_transmit(packet, count);
        if (sent < count) {
            for (size_t i = count; i > sent; --i) {
                tx_tail = tx_tail == 0u ? USB_TX_CAPACITY - 1u : tx_tail - 1u;
                tx_buffer[tx_tail] = packet[i - 1u];
            }
            COMPILER_MEMORY_BARRIER();
        }
    }
}

int py32_usb_available(void)
{
    uint16_t head = rx_head;
    uint16_t tail = rx_tail;
    return head >= tail ? (int)(head - tail) : (int)(USB_RX_CAPACITY - tail + head);
}

int py32_usb_peek(void)
{
    return rx_tail == rx_head ? -1 : rx_buffer[rx_tail];
}

int py32_usb_read(void)
{
    if (rx_tail == rx_head) {
        return -1;
    }
    uint8_t value = rx_buffer[rx_tail];
    COMPILER_MEMORY_BARRIER();
    rx_tail = ring_next(rx_tail, USB_RX_CAPACITY);
    return value;
}

size_t py32_usb_read_bytes(char *buffer, size_t length)
{
    size_t count = 0u;
    while (count < length) {
        int value = py32_usb_read();
        if (value < 0) {
            break;
        }
        buffer[count++] = (char)value;
    }
    return count;
}

size_t py32_usb_write(const uint8_t *buffer, size_t length)
{
    size_t count = 0u;
    while (count < length) {
        uint16_t next = ring_next(tx_head, USB_TX_CAPACITY);
        if (next == tx_tail) {
            py32_usb_task();
            next = ring_next(tx_head, USB_TX_CAPACITY);
            if (next == tx_tail) {
                break;
            }
        }
        tx_buffer[tx_head] = buffer[count++];
        COMPILER_MEMORY_BARRIER();
        tx_head = next;
    }
    py32_usb_task();
    return count;
}

void py32_usb_flush(void)
{
    while (tx_tail != tx_head) {
        py32_usb_task();
    }
}
