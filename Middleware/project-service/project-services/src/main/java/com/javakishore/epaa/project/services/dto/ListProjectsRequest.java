package com.javakishore.epaa.project.services.dto;

import com.javakishore.epaa.project.common.BaseRequest;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ListProjectsRequest extends BaseRequest {
    private int page = 1;
    private int pageSize = 15;
    private String search;   // matches name or client
}
