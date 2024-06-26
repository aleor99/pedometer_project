/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/

/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/

#ifndef __LIS3DH_H
    #define __LIS3DH_H

    /**
    *   \brief 7-bit I2C address of the slave device.
    */
    #define LIS3DH_DEVICE_ADDRESS 0x18 //global variable we use for the address

    /**
    *   \brief Address of the WHO AM I register
    */
    #define LIS3DH_WHO_AM_I_REG_ADDR 0x0F
    
    /**
    *   \brief WHOAMI return value
    */
    #define LIS3DH_WHOAMI_RETVAL     0x33

    /**
    *   \brief Address of the Status register
    */
    #define LIS3DH_STATUS_REG 0x27

    /**
    *   \brief Address of the Control register 1
    */
    #define LIS3DH_CTRL_REG1 0x20
    

    /**
    *   \brief Hex value to set normal mode to the accelerator
    */
    #define LIS3DH_NORMAL_MODE_CTRL_REG1 0x47
    
    /**
    *   \brief Hex value to set normal mode (powered off)
    **/
    #define LIS3DH_NORMAL_MODE_OFF_CTRL_REG1 0x07

    /**
    *   \brief  Address of the Temperature Sensor Configuration register
    */
    #define LIS3DH_TEMP_CFG_REG 0x1F 

    #define LIS3DH_TEMP_CFG_REG_ACTIVE 0xC0
   
    /////////////////////////////////////////////////
    #define LIS3DH_CTRL_REG2 0x21
    
    
    /////////////////////////////////////////////////
    #define LIS3DH_CTRL_REG3 0x22
    
    
    /////////////////////////////////////////////////
    
    // Brief Address of CTRL REG 4
    #define LIS3DH_CTRL_REG4 0x23
        
    // brief Block Data Update (BDU) Flag
    
    #define LIS3DH_CTRL_REG4_BDU_ACTIVE 0x80
    
    // Brief Address of CTRL REG 5
    
    #define LIS3DH_CTRL_REG5 0x24
    
    // Brief Address of FIFO CTRL REG
    
    #define LIS3DH_FIFO_CTRL_REG 0x2E
    
    // Brief Address of FIFO SRC REG
    #define LIS3DH_FIFO_SRC_REG 0x2F

    // Brief Address of the ADC output LSB register
    
    #define LIS3DH_OUT_ADC_3L 0x0C

    // Brief Address of the ADC output MSB register
    
    #define LIS3DH_OUT_ADC_3H 0x0D
    ////////////////////////////////////////////////
    //accelerations' registers 
    
    #define LIS3DH_OUT_ACCX_L 0X28
    #define LIS3DH_OUT_ACCX_H 0X29
    
    #define LIS3DH_OUT_ACCY_L 0X2A
    #define LIS3DH_OUT_ACCY_H 0X2B
    
    #define LIS3DH_OUT_ACCZ_L 0X2C
    #define LIS3DH_OUT_ACCZ_H 0X2D
    
#endif


/* [] END OF FILE */

