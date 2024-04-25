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

    CY_ISR_PROTO (Custom_ISR_RX); //qui i prototipi sono due, due isr quindi due isr 
    CY_ISR_PROTO (Custom_ISR_BUTTON);
    CY_ISR_PROTO (Custom_ISR_Timer);
    
    volatile uint8 Connessione_porta;
    volatile uint8 Invio_dati;
    volatile uint8 Errore_LIS;
    volatile uint32 steps;
   
    
    
#endif
/* [] END OF FILE */

