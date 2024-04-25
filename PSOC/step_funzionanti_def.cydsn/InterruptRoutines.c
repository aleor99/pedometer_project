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
#include "InterruptRoutines.h"
#include "project.h"
#include "UART_1.h"
#include "ssd1306.h"

#define BUFFER_SIZE 100
#define ON 1
#define OFF 0

int ch_received[BUFFER_SIZE];
volatile uint32 steps=0;
int invio_dati=OFF;
int count=0;
uint8 flag_first=1;
int press_stop=0;


CY_ISR (Custom_ISR_RX)
{
    char receivedChar = UART_1_GetChar();
    switch (receivedChar)
    {
        case 'c':
        case'C':
            Pin_LED_Write(1);
            Connessione_porta=1;
            PWM_LED_ACC_WriteCompare(255);
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Connection..");
            display_update(); 
            break;
        case's':
        case'S':
            Pin_LED_Write(0);
            Invio_dati=ON; 
            Connessione_porta=OFF;
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Steps: ");
            display_update();
            break;
        case 'P':
        case 'p':
            Invio_dati=OFF;
            break;
        case'z':
            steps++;                     
                break;
        default:   
            break;
    }   
}

CY_ISR (Custom_ISR_Timer)
{
    count++;
    Timer_ReadStatusRegister();
}

CY_ISR (Custom_ISR_BUTTON)
{
    if(flag_first==1)
    {
        count=0;
        flag_first=0;
    }
    else
    {
        press_stop=count;
        flag_first=1;
    }   
    if(press_stop>=5000)
    {
        CySoftwareReset();
        press_stop=0;
    }        
    Pin_BUTTON_ClearInterrupt();         
}



/* [] END OF FILE */

