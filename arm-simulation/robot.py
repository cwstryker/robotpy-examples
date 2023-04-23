#!/usr/bin/env python3
#
# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.

import math
import wpilib
import wpimath.controller


class MyRobot(wpilib.TimedRobot):
    """
    A robot program that controls an arm pivoting at the top of a tower.

    The arm position is controlled by Joystick 0 in Teleop mode only.
      - The Y-axis (i.e. Xbox left stick) controls the angle of the arm.
      - When pressed, the trigger button (i.e. A button) enables arm control, otherwise the arm motor is disabled.
    """

    kMotorPort = 0
    kEncoderAChannel = 0
    kEncoderBChannel = 1
    kJoystickPort = 0

    kArmPositionKey = "ArmPosition"
    kArmPKey = "ArmP"

    # distance per pulse = (angle per revolution) / (pulses per revolution)
    #  = (2 * PI rads) / (4096 pulses)
    kArmEncoderDistPerPulse = 2.0 * math.pi / 4096.0

    def robotInit(self) -> None:
        # The P gain for the PID controller that drives this arm.
        self.kArmKp = 50.0

        # The full scale deviation of the arm from horizontal (in degrees)
        self.armPosition = 75.0

        # standard classes for controlling our arm
        self.controller = wpimath.controller.PIDController(self.kArmKp, 0, 0)
        self.encoder = wpilib.Encoder(self.kEncoderAChannel, self.kEncoderBChannel)
        self.motor = wpilib.PWMSparkMax(self.kMotorPort)
        self.joystick = wpilib.Joystick(self.kJoystickPort)

        self.encoder.setDistancePerPulse(self.kArmEncoderDistPerPulse)

        # Set the Arm position setpoint and P constant to Preferences if the keys
        # don't already exist
        if not wpilib.Preferences.containsKey(self.kArmPositionKey):
            wpilib.Preferences.setDouble(self.kArmPositionKey, self.armPosition)
        if not wpilib.Preferences.containsKey(self.kArmPKey):
            wpilib.Preferences.setDouble(self.kArmPKey, self.kArmKp)

    def teleopInit(self) -> None:
        # Read Preferences for Arm setpoint and kP on entering Teleop
        self.armPosition = wpilib.Preferences.getDouble(
            self.kArmPositionKey, self.armPosition
        )
        if self.kArmKp != wpilib.Preferences.getDouble(self.kArmPKey, self.kArmKp):
            self.kArmKp = wpilib.Preferences.getDouble(self.kArmPKey, self.kArmKp)
            self.controller.setP(self.kArmKp)

    def teleopPeriodic(self) -> None:
        if self.joystick.getTrigger():
            # Here we run PID control like normal, with a setpoint read from
            # preferences in degrees
            pid_output = self.controller.calculate(
                self.encoder.getDistance(),
                math.radians(self.armPosition * -self.joystick.getY()),
            )
            self.motor.setVoltage(pid_output)
        else:
            # Otherwise we disable the motor
            self.motor.set(0.0)

    def disabledInit(self) -> None:
        # This just makes sure that our simulation code knows that the motor is off
        self.motor.set(0)


if __name__ == "__main__":
    wpilib.run(MyRobot)
