package com.javakishore.epaa.notification.services.dto;

import com.javakishore.epaa.notification.common.BaseRequest;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class CreateNotificationRequest extends BaseRequest {

    @NotBlank
    private String employeeId;

    private String allocationId;
    private String channel;
    private String subject;
    private String body;
}
