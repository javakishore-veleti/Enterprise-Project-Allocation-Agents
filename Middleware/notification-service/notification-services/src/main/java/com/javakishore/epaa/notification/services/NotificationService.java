package com.javakishore.epaa.notification.services;

import com.javakishore.epaa.notification.common.PageResponse;
import com.javakishore.epaa.notification.services.dto.CreateNotificationRequest;
import com.javakishore.epaa.notification.services.dto.ListNotificationsRequest;
import com.javakishore.epaa.notification.services.dto.NotificationResponse;

public interface NotificationService {

    NotificationResponse create(CreateNotificationRequest request);

    NotificationResponse get(String id);

    NotificationResponse deliver(String id);

    PageResponse<NotificationResponse> list(ListNotificationsRequest request);
}
