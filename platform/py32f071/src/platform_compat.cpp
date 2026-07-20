#include "rurp_platform.h"
#include "py32f071_board.h"

RurpSerialPort Serial;

void RurpSerialPort::begin(unsigned long baud) { (void)baud; }
void RurpSerialPort::end() {}
int RurpSerialPort::available() const { return py32_usb_available(); }
int RurpSerialPort::read() { return py32_usb_read(); }
int RurpSerialPort::peek() const { return py32_usb_peek(); }
size_t RurpSerialPort::readBytes(char *buffer, size_t length) { return py32_usb_read_bytes(buffer, length); }
size_t RurpSerialPort::write(uint8_t value) { return py32_usb_write(&value, 1u); }
size_t RurpSerialPort::write(const uint8_t *buffer, size_t length) { return py32_usb_write(buffer, length); }
size_t RurpSerialPort::write(const char *buffer, size_t length) { return py32_usb_write((const uint8_t *)buffer, length); }
size_t RurpSerialPort::print(const char *text) { return write(text, strlen(text)); }
size_t RurpSerialPort::println(const char *text)
{
    size_t count = print(text);
    static const uint8_t newline = '\n';
    return count + py32_usb_write(&newline, 1u);
}
void RurpSerialPort::flush() { py32_usb_flush(); }
RurpSerialPort::operator bool() const { return true; }
