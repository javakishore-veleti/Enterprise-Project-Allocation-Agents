package com.javakishore.epaa.notification.services;

public class NotificationNotFoundException extends RuntimeException {
    public NotificationNotFoundException(String id) {
        super("Notification not found: " + id);
    }
}
