package com.javakishore.epaa.notification.services.dto;

import com.javakishore.epaa.notification.common.BaseResponse;
import java.time.OffsetDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NotificationResponse extends BaseResponse {
    private String id;
    private String employeeId;
    private String allocationId;
    private String channel;
    private String subject;
    private String body;
    private String status;
    private OffsetDateTime createdAt;
}
