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
#ifndef __INTERRUPT_ROUTINES_H
    #define __INTERRUPT_ROUTNINES_H
    
    #include "cytypes.h"
    #include "stdio.h"
    #include <string.h>
    #include <ctype.h>
    
    #define BUFFER_SIZE 50
    #define OFF 0
    #define ON 1

    CY_ISR_PROTO (Custom_ISR_RX);  
    CY_ISR_PROTO (Custom_ISR_BUTTON);
    CY_ISR_PROTO (Custom_ISR_Timer);
    
    volatile uint8 Connessione_porta;
    volatile uint8 Invio_dati;
    volatile uint8 Errore_LIS;
    extern volatile char ch_received;
    extern char calories[];
    extern char velocity[];
    extern char distance[];
    extern char kcal[];
    extern volatile uint8 invio_OLED;
    extern volatile uint8 flag_v;
    extern volatile uint8 flag_d;
    extern volatile uint8 flag_k;
    extern volatile uint8 backup_v;
    extern volatile uint8 backup_d;
    extern volatile uint8 backup_k;
    extern volatile uint8 backup_s;
    volatile uint32 steps;
    
       
#endif
/* [] END OF FILE */

