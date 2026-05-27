package com.javakishore.epaa.employee.api;

import com.javakishore.epaa.employee.common.PageResponse;
import com.javakishore.epaa.employee.services.EmployeeService;
import com.javakishore.epaa.employee.services.dto.CreateEmployeeRequest;
import com.javakishore.epaa.employee.services.dto.EmployeeResponse;
import com.javakishore.epaa.employee.services.dto.ListEmployeesRequest;
import com.javakishore.epaa.employee.services.dto.UpdateEmployeeRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    private final EmployeeService service;

    public EmployeeController(EmployeeService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public EmployeeResponse create(@Valid @RequestBody CreateEmployeeRequest request) {
        return service.create(request);
    }

    @GetMapping("/{id}")
    public EmployeeResponse get(@PathVariable String id) {
        return service.get(id);
    }

    @PutMapping("/{id}")
    public EmployeeResponse update(@PathVariable String id, @Valid @RequestBody UpdateEmployeeRequest request) {
        request.setId(id);
        return service.update(request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String id) {
        service.delete(id);
    }

    @GetMapping
    public PageResponse<EmployeeResponse> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "15") int pageSize,
            @RequestParam(required = false) String search) {
        ListEmployeesRequest request = new ListEmployeesRequest();
        request.setPage(page);
        request.setPageSize(pageSize);
        request.setSearch(search);
        return service.list(request);
    }
}
