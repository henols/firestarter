#include "py32f071_board.h"
#include "py32f071_regs.h"

static uint8_t g_control_shadow;

static py32_gpio_t *data_port(void)
{
    return PY32_GPIOB;
}

static py32_gpio_t *control_port(void)
{
    return PY32_GPIOC;
}

static void set_pin_mode(py32_gpio_t *port, uint32_t pin, uint32_t mode)
{
    uint32_t shift = pin * 2u;
    uint32_t value = port->MODER;
    value &= ~(3u << shift);
    value |= (mode & 3u) << shift;
    port->MODER = value;
}

void py32_gpio_init(void)
{
    /* Enable GPIOA/B/C. */
    PY32_RCC->IOPENR |= PY32_BIT(0) | PY32_BIT(1) | PY32_BIT(2);

    rurp_set_data_input();

    for (uint32_t pin = PY32_CTRL_PIN_SHIFT; pin < PY32_CTRL_PIN_SHIFT + 8u; ++pin) {
        set_pin_mode(control_port(), pin, 1u);
    }
    control_port()->OTYPER &= ~(0xFFu << PY32_CTRL_PIN_SHIFT);
    control_port()->OSPEEDR |= 0xFFFFu << (PY32_CTRL_PIN_SHIFT * 2u);

    set_pin_mode(PY32_GPIOA, PY32_VPP_ENABLE_PIN, 1u);
    PY32_GPIOA->BSRR = PY32_BIT(PY32_VPP_ENABLE_PIN + 16u);

    set_pin_mode(PY32_GPIOC, PY32_USER_BUTTON_PIN, 0u);
    PY32_GPIOC->PUPDR = (PY32_GPIOC->PUPDR & ~(3u << (PY32_USER_BUTTON_PIN * 2u))) |
                        (1u << (PY32_USER_BUTTON_PIN * 2u));

    g_control_shadow = 0u;
    control_port()->BSRR = 0xFFu << (PY32_CTRL_PIN_SHIFT + 16u);
}

void rurp_set_data_output(void)
{
    py32_gpio_t *port = data_port();
    uint32_t mask = 0xFFFFu << (PY32_DATA_PIN_SHIFT * 2u);
    uint32_t modes = 0x5555u << (PY32_DATA_PIN_SHIFT * 2u);
    port->MODER = (port->MODER & ~mask) | modes;
    port->OTYPER &= ~(0xFFu << PY32_DATA_PIN_SHIFT);
    port->PUPDR &= ~mask;
}

void rurp_set_data_input(void)
{
    py32_gpio_t *port = data_port();
    uint32_t mask = 0xFFFFu << (PY32_DATA_PIN_SHIFT * 2u);
    port->MODER &= ~mask;
    port->PUPDR &= ~mask;
}

void rurp_write_data_buffer(uint8_t data)
{
    uint32_t set_mask = ((uint32_t)data) << PY32_DATA_PIN_SHIFT;
    uint32_t clear_mask = ((uint32_t)(~data) & 0xFFu) << (PY32_DATA_PIN_SHIFT + 16u);
    rurp_set_data_output();
    data_port()->BSRR = set_mask | clear_mask;
}

uint8_t rurp_read_data_buffer(void)
{
    uint32_t snapshot = data_port()->IDR;
    return (uint8_t)((snapshot >> PY32_DATA_PIN_SHIFT) & 0xFFu);
}

void rurp_set_control_pin(uint8_t logical_pin, uint8_t state)
{
    if (state != 0u) {
        g_control_shadow |= logical_pin;
    } else {
        g_control_shadow &= (uint8_t)~logical_pin;
    }

    uint32_t set_mask = ((uint32_t)g_control_shadow) << PY32_CTRL_PIN_SHIFT;
    uint32_t clear_mask = ((uint32_t)(~g_control_shadow) & 0xFFu) << (PY32_CTRL_PIN_SHIFT + 16u);
    control_port()->BSRR = set_mask | clear_mask;
}

uint8_t rurp_user_button_pressed(void)
{
    return (PY32_GPIOC->IDR & PY32_BIT(PY32_USER_BUTTON_PIN)) == 0u;
}
