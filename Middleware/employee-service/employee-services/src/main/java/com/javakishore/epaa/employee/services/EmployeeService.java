package com.javakishore.epaa.employee.services;

import com.javakishore.epaa.employee.common.PageResponse;
import com.javakishore.epaa.employee.services.dto.CreateEmployeeRequest;
import com.javakishore.epaa.employee.services.dto.EmployeeResponse;
import com.javakishore.epaa.employee.services.dto.ListEmployeesRequest;
import com.javakishore.epaa.employee.services.dto.UpdateEmployeeRequest;

/**
 * Employee use cases. Every method takes a single Request DTO (or an identifier)
 * and returns a single Response DTO — never long scalar parameter lists.
 */
public interface EmployeeService {

    EmployeeResponse create(CreateEmployeeRequest request);

    EmployeeResponse get(String id);

    EmployeeResponse update(UpdateEmployeeRequest request);

    void delete(String id);

    PageResponse<EmployeeResponse> list(ListEmployeesRequest request);
}
