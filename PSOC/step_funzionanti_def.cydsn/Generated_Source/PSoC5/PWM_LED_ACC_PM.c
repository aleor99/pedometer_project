/*******************************************************************************
* File Name: PWM_LED_ACC_PM.c
* Version 3.30
*
* Description:
*  This file provides the power management source code to API for the
*  PWM.
*
* Note:
*
********************************************************************************
* Copyright 2008-2014, Cypress Semiconductor Corporation.  All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/

#include "PWM_LED_ACC.h"

static PWM_LED_ACC_backupStruct PWM_LED_ACC_backup;


/*******************************************************************************
* Function Name: PWM_LED_ACC_SaveConfig
********************************************************************************
*
* Summary:
*  Saves the current user configuration of the component.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_LED_ACC_backup:  Variables of this global structure are modified to
*  store the values of non retention configuration registers when Sleep() API is
*  called.
*
*******************************************************************************/
void PWM_LED_ACC_SaveConfig(void) 
{

    #if(!PWM_LED_ACC_UsingFixedFunction)
        #if(!PWM_LED_ACC_PWMModeIsCenterAligned)
            PWM_LED_ACC_backup.PWMPeriod = PWM_LED_ACC_ReadPeriod();
        #endif /* (!PWM_LED_ACC_PWMModeIsCenterAligned) */
        PWM_LED_ACC_backup.PWMUdb = PWM_LED_ACC_ReadCounter();
        #if (PWM_LED_ACC_UseStatus)
            PWM_LED_ACC_backup.InterruptMaskValue = PWM_LED_ACC_STATUS_MASK;
        #endif /* (PWM_LED_ACC_UseStatus) */

        #if(PWM_LED_ACC_DeadBandMode == PWM_LED_ACC__B_PWM__DBM_256_CLOCKS || \
            PWM_LED_ACC_DeadBandMode == PWM_LED_ACC__B_PWM__DBM_2_4_CLOCKS)
            PWM_LED_ACC_backup.PWMdeadBandValue = PWM_LED_ACC_ReadDeadTime();
        #endif /*  deadband count is either 2-4 clocks or 256 clocks */

        #if(PWM_LED_ACC_KillModeMinTime)
             PWM_LED_ACC_backup.PWMKillCounterPeriod = PWM_LED_ACC_ReadKillTime();
        #endif /* (PWM_LED_ACC_KillModeMinTime) */

        #if(PWM_LED_ACC_UseControl)
            PWM_LED_ACC_backup.PWMControlRegister = PWM_LED_ACC_ReadControlRegister();
        #endif /* (PWM_LED_ACC_UseControl) */
    #endif  /* (!PWM_LED_ACC_UsingFixedFunction) */
}


/*******************************************************************************
* Function Name: PWM_LED_ACC_RestoreConfig
********************************************************************************
*
* Summary:
*  Restores the current user configuration of the component.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_LED_ACC_backup:  Variables of this global structure are used to
*  restore the values of non retention registers on wakeup from sleep mode.
*
*******************************************************************************/
void PWM_LED_ACC_RestoreConfig(void) 
{
        #if(!PWM_LED_ACC_UsingFixedFunction)
            #if(!PWM_LED_ACC_PWMModeIsCenterAligned)
                PWM_LED_ACC_WritePeriod(PWM_LED_ACC_backup.PWMPeriod);
            #endif /* (!PWM_LED_ACC_PWMModeIsCenterAligned) */

            PWM_LED_ACC_WriteCounter(PWM_LED_ACC_backup.PWMUdb);

            #if (PWM_LED_ACC_UseStatus)
                PWM_LED_ACC_STATUS_MASK = PWM_LED_ACC_backup.InterruptMaskValue;
            #endif /* (PWM_LED_ACC_UseStatus) */

            #if(PWM_LED_ACC_DeadBandMode == PWM_LED_ACC__B_PWM__DBM_256_CLOCKS || \
                PWM_LED_ACC_DeadBandMode == PWM_LED_ACC__B_PWM__DBM_2_4_CLOCKS)
                PWM_LED_ACC_WriteDeadTime(PWM_LED_ACC_backup.PWMdeadBandValue);
            #endif /* deadband count is either 2-4 clocks or 256 clocks */

            #if(PWM_LED_ACC_KillModeMinTime)
                PWM_LED_ACC_WriteKillTime(PWM_LED_ACC_backup.PWMKillCounterPeriod);
            #endif /* (PWM_LED_ACC_KillModeMinTime) */

            #if(PWM_LED_ACC_UseControl)
                PWM_LED_ACC_WriteControlRegister(PWM_LED_ACC_backup.PWMControlRegister);
            #endif /* (PWM_LED_ACC_UseControl) */
        #endif  /* (!PWM_LED_ACC_UsingFixedFunction) */
    }


/*******************************************************************************
* Function Name: PWM_LED_ACC_Sleep
********************************************************************************
*
* Summary:
*  Disables block's operation and saves the user configuration. Should be called
*  just prior to entering sleep.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_LED_ACC_backup.PWMEnableState:  Is modified depending on the enable
*  state of the block before entering sleep mode.
*
*******************************************************************************/
void PWM_LED_ACC_Sleep(void) 
{
    #if(PWM_LED_ACC_UseControl)
        if(PWM_LED_ACC_CTRL_ENABLE == (PWM_LED_ACC_CONTROL & PWM_LED_ACC_CTRL_ENABLE))
        {
            /*Component is enabled */
            PWM_LED_ACC_backup.PWMEnableState = 1u;
        }
        else
        {
            /* Component is disabled */
            PWM_LED_ACC_backup.PWMEnableState = 0u;
        }
    #endif /* (PWM_LED_ACC_UseControl) */

    /* Stop component */
    PWM_LED_ACC_Stop();

    /* Save registers configuration */
    PWM_LED_ACC_SaveConfig();
}


/*******************************************************************************
* Function Name: PWM_LED_ACC_Wakeup
********************************************************************************
*
* Summary:
*  Restores and enables the user configuration. Should be called just after
*  awaking from sleep.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_LED_ACC_backup.pwmEnable:  Is used to restore the enable state of
*  block on wakeup from sleep mode.
*
*******************************************************************************/
void PWM_LED_ACC_Wakeup(void) 
{
     /* Restore registers values */
    PWM_LED_ACC_RestoreConfig();

    if(PWM_LED_ACC_backup.PWMEnableState != 0u)
    {
        /* Enable component's operation */
        PWM_LED_ACC_Enable();
    } /* Do nothing if component's block was disabled before */

}


/* [] END OF FILE */
