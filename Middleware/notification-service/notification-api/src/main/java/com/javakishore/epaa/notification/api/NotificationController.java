package com.javakishore.epaa.notification.api;

import com.javakishore.epaa.notification.common.PageResponse;
import com.javakishore.epaa.notification.services.NotificationService;
import com.javakishore.epaa.notification.services.dto.CreateNotificationRequest;
import com.javakishore.epaa.notification.services.dto.ListNotificationsRequest;
import com.javakishore.epaa.notification.services.dto.NotificationResponse;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/notifications")
public class NotificationController {

    private final NotificationService service;

    public NotificationController(NotificationService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public NotificationResponse create(@Valid @RequestBody CreateNotificationRequest request) {
        return service.create(request);
    }

    @GetMapping("/{id}")
    public NotificationResponse get(@PathVariable String id) {
        return service.get(id);
    }

    @PostMapping("/{id}/deliver")
    public NotificationResponse deliver(@PathVariable String id) {
        return service.deliver(id);
    }

    @GetMapping
    public PageResponse<NotificationResponse> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "15") int pageSize,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String employeeId) {
        ListNotificationsRequest request = new ListNotificationsRequest();
        request.setPage(page);
        request.setPageSize(pageSize);
        request.setStatus(status);
        request.setEmployeeId(employeeId);
        return service.list(request);
    }
}
