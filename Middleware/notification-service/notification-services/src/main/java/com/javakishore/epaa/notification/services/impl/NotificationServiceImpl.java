package com.javakishore.epaa.notification.services.impl;

import com.javakishore.epaa.notification.common.PageResponse;
import com.javakishore.epaa.notification.dao.NotificationRepository;
import com.javakishore.epaa.notification.entities.NotificationEntity;
import com.javakishore.epaa.notification.services.NotificationNotFoundException;
import com.javakishore.epaa.notification.services.NotificationService;
import com.javakishore.epaa.notification.services.dto.CreateNotificationRequest;
import com.javakishore.epaa.notification.services.dto.ListNotificationsRequest;
import com.javakishore.epaa.notification.services.dto.NotificationResponse;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class NotificationServiceImpl implements NotificationService {

    private static final Logger log = LoggerFactory.getLogger(NotificationServiceImpl.class);

    private final NotificationRepository repository;

    public NotificationServiceImpl(NotificationRepository repository) {
        this.repository = repository;
    }

    @Override
    public NotificationResponse create(CreateNotificationRequest r) {
        NotificationEntity n = new NotificationEntity();
        n.setEmployeeId(r.getEmployeeId());
        n.setAllocationId(r.getAllocationId());
        n.setChannel(r.getChannel() != null ? r.getChannel() : "log");
        n.setSubject(r.getSubject());
        n.setBody(r.getBody());
        n.setStatus("queued");
        return toResponse(repository.save(n));
    }

    @Override
    @Transactional(readOnly = true)
    public NotificationResponse get(String id) {
        return repository.findById(id).map(this::toResponse)
                .orElseThrow(() -> new NotificationNotFoundException(id));
    }

    @Override
    public NotificationResponse deliver(String id) {
        NotificationEntity n = repository.findById(id)
                .orElseThrow(() -> new NotificationNotFoundException(id));
        // Local "delivery" is a log line (SMTP/Slack stubbed); SES on AWS later.
        log.info("[notify:{}] to employee={} subject='{}' :: {}",
                n.getChannel(), n.getEmployeeId(), n.getSubject(), n.getBody());
        n.setStatus("delivered");
        return toResponse(repository.save(n));
    }

    @Override
    @Transactional(readOnly = true)
    public PageResponse<NotificationResponse> list(ListNotificationsRequest r) {
        int page = Math.max(r.getPage(), 1);
        Pageable pageable = PageRequest.of(page - 1, r.getPageSize(),
                Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<NotificationEntity> result;
        if (r.getStatus() != null && !r.getStatus().isBlank()) {
            result = repository.findByStatus(r.getStatus(), pageable);
        } else if (r.getEmployeeId() != null && !r.getEmployeeId().isBlank()) {
            result = repository.findByEmployeeId(r.getEmployeeId(), pageable);
        } else {
            result = repository.findAll(pageable);
        }
        List<NotificationResponse> items = result.getContent().stream().map(this::toResponse).toList();
        return PageResponse.<NotificationResponse>builder()
                .items(items).page(page).pageSize(r.getPageSize())
                .total(result.getTotalElements()).pages(result.getTotalPages()).build();
    }

    private NotificationResponse toResponse(NotificationEntity n) {
        return NotificationResponse.builder()
                .id(n.getId()).employeeId(n.getEmployeeId()).allocationId(n.getAllocationId())
                .channel(n.getChannel()).subject(n.getSubject()).body(n.getBody())
                .status(n.getStatus()).createdAt(n.getCreatedAt()).build();
    }
}
