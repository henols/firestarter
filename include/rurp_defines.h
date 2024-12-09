#ifndef RURP_DEFINES_H
#define RURP_DEFINES_H

#include "config.h"

// CONTROL REGISTER
#ifndef HARDWARE_REVISION
#define VPE_TO_VPP      0x01
#define A16             VPE_TO_VPP
#define A9_VPP_ENABLE   0x02
#define VPE_ENABLE      0x04
#define P1_VPP_ENABLE   0x08
#define A17             0x10
#define A18             0x20
#define RW              0x40
#define REGULATOR       0x80

#else
#define REVISION_0 0
#define REVISION_1 1
#define REVISION_2 2

#define A16             0x01
#define A9_VPP_ENABLE   0x02
#define VPE_ENABLE      0x04
#define P1_VPP_ENABLE   0x08
#define A17             0x10
#define A18             0x20
#define RW              0x40
#define REGULATOR       0x80
#define VPE_TO_VPP      0x100

#endif

#define A13             0x20
#ifdef HARDWARE_REVISION

// REV 1
#define REV_1_VPE_TO_VPP      0x01
#define REV_1_A9_VPP_ENABLE   0x02
#define REV_1_VPE_ENABLE      0x04
#define REV_1_P1_VPP_ENABLE   0x08
#define REV_1_RW              0x40
#define REV_1_REGULATOR       0x80

#define REV_1_A16             REV_1_VPE_TO_VPP
#define REV_1_A17             0x10
#define REV_1_A18             0x20

// REV 2
#define REV_2_VPE_TO_VPP      0x01
#define REV_2_A9_VPP_ENABLE   0x02
#define REV_2_VPE_ENABLE      0x04
#define REV_2_P1_VPP_ENABLE   0x08
#define REV_2_P30             0x10
#define REV_2_P2              0x20
#define REV_2_P31             0x40
#define REV_2_REGULATOR       0x80

#define REV_2_P1              P1_VPP_ENABLE
#define REV_2_RW              REV_2_P31
#define REV_2_A16             REV_2_P2
#define REV_2_A17             REV_2_P30
#define REV_2_A18             P1_VPP_ENABLE
#endif

#endif