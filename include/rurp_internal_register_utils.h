#ifndef __RURP_REGESTERS_UTILS_H__
#define __RURP_REGESTERS_UTILS_H__

#include "rurp_shield.h"

// Function to write data to a specific register on the RURP shield.
// This is an internal function used by rurp_write_to_register.
// 
// Parameters:
//   reg: The register to write to (e.g., LEAST_SIGNIFICANT_BYTE, MOST_SIGNIFICANT_BYTE, CONTROL_REGISTER).
//   data: The data to write to the register.
void rurp_internal_write_to_register(uint8_t reg, rurp_register_t data);



#endif // __RURP_REGESTERS_UTILS_H__