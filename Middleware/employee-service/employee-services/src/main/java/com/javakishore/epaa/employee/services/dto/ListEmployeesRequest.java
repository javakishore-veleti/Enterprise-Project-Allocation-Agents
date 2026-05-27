package com.javakishore.epaa.employee.services.dto;

import com.javakishore.epaa.employee.common.BaseRequest;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** Paginated, searchable employee listing request. */
@Getter
@Setter
@NoArgsConstructor
public class ListEmployeesRequest extends BaseRequest {
    private int page = 1;          // 1-based
    private int pageSize = 15;
    private String search;         // matches full name or title
}
