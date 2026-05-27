package com.javakishore.epaa.notification.entities;

import com.javakishore.epaa.notification.common.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "notifications")
@Getter
@Setter
public class NotificationEntity extends BaseEntity {

    @Column(name = "employee_id", nullable = false, length = 36)
    private String employeeId;

    @Column(name = "allocation_id", length = 36)
    private String allocationId;

    @Column(name = "channel", length = 30)
    private String channel;   // log | email | slack

    @Column(name = "subject", length = 200)
    private String subject;

    @Column(name = "body", columnDefinition = "text")
    private String body;

    @Column(name = "status", length = 30)
    private String status;    // queued | delivered | failed
}
