//* ========================================
//* ========================================
//* ========================================
//* ========================================
//* ========================================
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


char velocity_car[BUFFER_SIZE]="Velocity: ...";
char distance_car[BUFFER_SIZE]="Distance: ...";
char calories_car[BUFFER_SIZE]="Calories: ...";
char velocity[BUFFER_SIZE];
char calories[BUFFER_SIZE];
char distance[BUFFER_SIZE];
volatile char ch_received;
volatile uint32 steps=0;
volatile int button_count=0;
volatile int count=0;
volatile int press_stop=0;
volatile int i=0;
volatile uint8 invio_OLED=OFF;
volatile uint8 flag_v=OFF;
volatile uint8 flag_d=OFF;
volatile uint8 flag_k=OFF;
volatile uint8 backup_s=OFF;
volatile uint8 backup_v=OFF;
volatile uint8 backup_d=OFF;
volatile uint8 backup_k=OFF;
uint8 flag_first=ON;


CY_ISR (Custom_ISR_RX)
{
    char receivedChar = UART_1_GetChar();
    switch (receivedChar)
    {
        case 'c':
        case'C':
            Pin_LED_Write(ON);
            Connessione_porta=ON;
            PWM_LED_ACC_WriteCompare(255);
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Connection...");
            display_update(); 
            break;
        case's':
        case'S':
            Pin_LED_Write(OFF);
            Invio_dati=ON; 
            Connessione_porta=OFF;
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Steps: ");
            display_update();
            backup_s=ON;
            break;
        case 'P':
        case 'p':
            Invio_dati=OFF;
            break;
        case'z':
            steps++;
            break;
        case 'v':
            flag_v=ON;
            for (i = 0; i < BUFFER_SIZE; i++) 
            {
                velocity[i] = '\0';
                
            } 
            break;
        case 'd':                
            flag_d=ON;             
            for (i = 0; i < BUFFER_SIZE; i++) 
            {
                distance[i] = '\0';
            } 
            break;
        case 'k':
            flag_k=ON;            
            for (i = 0; i < BUFFER_SIZE; i++) 
            {
                calories[i] = '\0';
            }
            break;
        case '\n':
            invio_OLED=ON;
            break; 
        default: 
            break;
    }
    if(flag_k==ON)
    {          
        strcat(calories, &receivedChar); 
    }
    if (flag_d==ON)
    {
        strcat(distance, &receivedChar);
    }
        
    if(flag_v==ON)
    {
        strcat(velocity, &receivedChar);
    }
}

CY_ISR (Custom_ISR_Timer) //TIMER interrupt for the reset's control
{
    count++;
    Timer_ReadStatusRegister();
}

CY_ISR (Custom_ISR_BUTTON)//ISR for the button control
{
    
    if(flag_first==ON)
    {
        count=0;
        flag_first=OFF;
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
    switch(button_count)
    {
        case 0://step 
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Steps: ...");
            display_update();
            backup_k=OFF;
            backup_s=ON;
            break;
        case 2://distance
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Distance: ...");
            display_update();
            backup_s=OFF;
            backup_d=ON;
            break;
        case 4://velocity
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Velocity: ...");
            display_update();
            backup_v=ON;
            backup_d=OFF;
            break;
        case 6://calories
            display_clear();    
            display_update();    
            gfx_setTextSize(2);
            gfx_setTextColor(WHITE);
            gfx_setCursor(2,2);
            gfx_println("Calories: ...");
            display_update();
            backup_v=OFF;
            backup_k=ON;
            break;
        default:
            break;
    }
    if (button_count==6)
    {
        button_count=0;
    }
    else
    {
        button_count++;
    }          
    Pin_BUTTON_ClearInterrupt();         
}

/* [] END OF FILE */