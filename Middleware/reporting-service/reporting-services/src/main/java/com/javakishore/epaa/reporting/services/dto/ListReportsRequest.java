package com.javakishore.epaa.reporting.services.dto;

import com.javakishore.epaa.reporting.common.BaseRequest;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ListReportsRequest extends BaseRequest {
    private int page = 1;
    private int pageSize = 15;
    private String projectId;   // optional filter
}
