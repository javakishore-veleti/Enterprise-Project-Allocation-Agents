package com.javakishore.epaa.employee.services;

public class EmployeeNotFoundException extends RuntimeException {
    public EmployeeNotFoundException(String id) {
        super("Employee not found: " + id);
    }
}
