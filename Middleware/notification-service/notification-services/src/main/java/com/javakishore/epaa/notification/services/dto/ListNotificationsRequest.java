package com.javakishore.epaa.notification.services.dto;

import com.javakishore.epaa.notification.common.BaseRequest;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ListNotificationsRequest extends BaseRequest {
    private int page = 1;
    private int pageSize = 15;
    private String status;       // optional filter
    private String employeeId;   // optional filter
}
