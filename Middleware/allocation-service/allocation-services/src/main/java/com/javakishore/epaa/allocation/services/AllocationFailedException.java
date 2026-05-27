package com.javakishore.epaa.allocation.services;

public class AllocationFailedException extends RuntimeException {
    public AllocationFailedException(String message, Throwable cause) {
        super(message, cause);
    }
}
