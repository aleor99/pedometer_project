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
#include <stdio.h>
#include "project.h"
#include "I2C_Interface.h"
#include "LIS3DH.h"
#include "InterruptRoutines.h"
#include "isr_RX.h"
#include "ssd1306.h"


#define ON 1
#define OFF 0
#define DISPLAY_ADDRESS 0x3D

char message[50] = {'\0'};

int main(void)
{
    CyGlobalIntEnable; /* Enable global interrupts. */
    
    I2C_Peripheral_Start();
    display_init(DISPLAY_ADDRESS);
    UART_1_Start();
    PWM_LED_ACC_Start();
    
    //Grafica di accensione 
    int16_t j;
    for( j = 0 ; j < gfx_height() ; j += 2 ){
            gfx_drawCircle( gfx_width()/2, gfx_height()/2, j, WHITE );
            display_update();    
        }    

        CyDelay(3000);
        
        display_clear();    
        display_update(); 
    
        CyDelay(5);
        display_clear();    
        display_update();    
        gfx_setTextSize(2);
        gfx_setTextColor(WHITE);
        gfx_setCursor(2,2);
        gfx_println("Hey there!");
        display_update(); 
    
    
    //**Check if LIS3DH is connected**//     
    uint32_t rval = I2C_Master_MasterSendStart(LIS3DH_DEVICE_ADDRESS, I2C_Master_WRITE_XFER_MODE);
    if( rval == I2C_Master_MSTR_NO_ERROR ) {
    }
    I2C_Master_MasterSendStop();
    
    // String to print out messages over UART

    
    CyDelay(10);
    
    
    /******************************************/
    /*            I2C Reading                 */
    /******************************************/
          
//**I2C Master Read - WHOAMI Register **//
    uint8_t whoami_reg;
    ErrorCode error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, 
                                                  LIS3DH_WHO_AM_I_REG_ADDR,
                                                  &whoami_reg);
    if( error == ERROR ) {
        Pin_LED_CMT_Write(ON);
    }
    //if the comunication is not correct, so if the accelerometer register is not red correctly 
    //the LED is switched on 
    
      
    //**I2C Master Read - CTRL Register 1 **//
        
    /*       control_reg1: 0x47           */
    /*         ODR[3:0]-->0100            */
    /*      LPen-->DefaultValue:0         */
    /*   Zen,Yen,Xen-->DefaultValue:1     */
    
    
    uint8_t control_reg;
    error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, 
                                        LIS3DH_CTRL_REG1,
                                        &control_reg);
    control_reg |= 0x47; // sampling 50Hz
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG1,
                                         control_reg);     
    //*   I2C Temperature CTRL REG 4 Writing from LIS3DH   **//
    /*       control_reg2: 0x80               */
    /*              BDU-->1                   */
    /*        BLE-->DefaultValue:0            */
    /*       FS-->DefaultValue:00             */
    /*        HR-->DefaultValue:0             */
    /*      ST[1:0]-->DefaultValue:00         */
    /*        SIM-->DefaultValue:0            */    
    

//*   I2C Temperature CTRL REG 4 Writing from LIS3DH   **//
    /*       control_reg2: 0x80               */
    /*              BDU-->1                   */
    /*        BLE-->DefaultValue:0            */
    /*       FS-->DefaultValue:00             */
    /*        HR-->DefaultValue:0             */
    /*      ST[1:0]-->DefaultValue:00         */
    /*        SIM-->DefaultValue:0            */
    
    uint8_t ctrl_reg4; // Ctrl Register variable
    error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS,
                                        LIS3DH_CTRL_REG4,
                                        &ctrl_reg4);
    ctrl_reg4 |= LIS3DH_CTRL_REG4_BDU_ACTIVE; // must be changed to the appropriate value
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG4,
                                         ctrl_reg4);
  
    //* SETTING DEL FIFO *//
    
    /////////* ctrl_reg5: 0x40 */////////
    /*   BOOT --> Default value:0      */
    /*   FIFO_EN --> 1                 */
    /*   LIR_INT1 --> Default value: 0 */
    /*   D4D_INT1 --> Default value: 0 */
    /*   LIR_INT2 --> Default value: 0 */
    /*   D4D_INT2 --> Default value: 0 */
    
    uint8_t ctrl_reg5; // Ctrl Register variable
    
    error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS,
                                        LIS3DH_CTRL_REG5,
                                        &ctrl_reg5);
    ctrl_reg5 |= 0x40; // enable del FIFO
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG5,
                                         ctrl_reg5); 
    
    
    /////////* FIFO_CTRL_REG: 0x40 *////////
    /*   FM[1:0] --> 01 (FIFO mode)     */
    /*   TR --> Default value: 0          */
    /*   FTH[4:0] --> Default value: 0000 */
    
    uint8_t FIFO_ctrl_reg;
    
    error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS,
                                        LIS3DH_FIFO_CTRL_REG,
                                        &FIFO_ctrl_reg);
    FIFO_ctrl_reg |= 0x40; //FIFO mode (FM = 01)
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_FIFO_CTRL_REG,
                                         FIFO_ctrl_reg); 
    
    
   //Raw temperature data buffer
    uint8_t AccData[2]; //for the two register in which are contained the 10 bits 
    int16_t OutAcc;//variable will see in coolterm
    
    uint8_t FIFO_src_reg; 
    uint8_t FIFO_overrun; //variabile per controllare l'overrun
    //uint8_t FIFO_unread_samples;
    
    uint8_t i=0;
    uint8_t accelerazioni_multi[192];
    uint8_t flag_ci=OFF;
    

    
//**Starting of interrupts**//
    isr_RX_StartEx(Custom_ISR_RX);
    isr_BUTTON_StartEx(Custom_ISR_BUTTON);
    isr_Timer_StartEx(Custom_ISR_Timer);
    Timer_Start();
    
    for(;;)
    {
        if(Connessione_porta)
        {
            sprintf(message, "h ");
            UART_1_PutString(message);
            Connessione_porta=0;        
        }
        //When, from the GUI, the signal arrives to start the data reading 
        if (Invio_dati)
        {
            //Check FIFO overrun --> once is full teh reading starts
            error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS,
                                                  LIS3DH_FIFO_SRC_REG,
                                                    &FIFO_src_reg);
            if((error!=NO_ERROR)&(flag_ci==OFF))
            {
                    Pin_LED_CMT_Write(ON);
                    sprintf(message, "Comunication interrupted, please restart the psoc\n\r");//ricordarsi nella gui se arriva questo
                    UART_1_PutString(message);
                    flag_ci=ON;        
            }
            else if(error==NO_ERROR)
            {
                FIFO_overrun = FIFO_src_reg & 0x40; //l'overrun è dato dal secondo bit del registro
                if(FIFO_overrun == 0x40)/*&(error==NO_ERROR)*/
                {
                    flag_ci=OFF;
                    
                    Pin_LED_CMT_Write(OFF);
                    
                    
                    //Reading of the data 
                    error = I2C_Peripheral_ReadRegisterMulti(LIS3DH_DEVICE_ADDRESS,
                                                             LIS3DH_OUT_ACCX_L,
                                                             192,
                                                             accelerazioni_multi);

                    //Single accelerations' computation
                    for(i=0; i<32; i++)
                    {
                        if(error == NO_ERROR)
                        {
                            //Acceleration along x axis: positions  0-1, 6-7, 12-13, ...
                            AccData[0]=accelerazioni_multi[6*i];   
                            AccData[1]=accelerazioni_multi[6*i+1];
                            OutAcc = (int16) (AccData[0] | (AccData[1] << 8)) >> 6;
                            OutAcc=(OutAcc*4);
                            sprintf(message, "Accx Output: %d mg\r\n", OutAcc);
                            UART_1_PutString(message);
                            
                            //Acceleration along y axis: positions 2-3, 8-9, 14-15, ...
                            AccData[0]=accelerazioni_multi[6*i+2];
                            AccData[1]=accelerazioni_multi[6*i+3];
                            OutAcc = (int16) (AccData[0] | (AccData[1] << 8)) >> 6;
                            OutAcc=(OutAcc*4);
                            sprintf(message, "Accy Output: %d mg \r\n", OutAcc);
                            UART_1_PutString(message);
                            
                            //Acceleration along z axis: positions 4-5, 10-11, 16-17, ...
                            AccData[0]=accelerazioni_multi[6*i+4];
                            AccData[1]=accelerazioni_multi[6*i+5];
                            OutAcc = (int16) (AccData[0] | (AccData[1] << 8)) >> 6;
                            OutAcc=(OutAcc*4);
                            sprintf(message, "Accz Output: %d mg\r\n", OutAcc);
                            UART_1_PutString(message);
                        }
                    }
                                                             
                    //FIFO's reset
                    FIFO_ctrl_reg &= 0x00; //Bypass mode
                    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                                         LIS3DH_FIFO_CTRL_REG,
                                                         FIFO_ctrl_reg); 
                    CyDelay(100);
                    
                    FIFO_ctrl_reg |= 0x40; //FIFO mode (FM = 01)
                    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                                         LIS3DH_FIFO_CTRL_REG,
                                                         FIFO_ctrl_reg); 
                    
                    sprintf(message,"Steps: %lu",steps);
                    display_clear();    
                    display_update();    
                    gfx_setTextSize(2);
                    gfx_setTextColor(WHITE);
                    gfx_setCursor(2,2);
                    gfx_println(message);
                    display_update();    
                }
            }
        }
    }
}



/* [] END OF FILE */

