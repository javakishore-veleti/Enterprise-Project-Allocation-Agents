package com.javakishore.epaa.employee.services.impl;

import com.javakishore.epaa.employee.common.PageResponse;
import com.javakishore.epaa.employee.dao.EmployeeRepository;
import com.javakishore.epaa.employee.entities.EmployeeEntity;
import com.javakishore.epaa.employee.services.EmployeeNotFoundException;
import com.javakishore.epaa.employee.services.EmployeeService;
import com.javakishore.epaa.employee.services.dto.CreateEmployeeRequest;
import com.javakishore.epaa.employee.services.dto.EmployeeResponse;
import com.javakishore.epaa.employee.services.dto.ListEmployeesRequest;
import com.javakishore.epaa.employee.services.dto.UpdateEmployeeRequest;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class EmployeeServiceImpl implements EmployeeService {

    private final EmployeeRepository repository;

    public EmployeeServiceImpl(EmployeeRepository repository) {
        this.repository = repository;
    }

    @Override
    public EmployeeResponse create(CreateEmployeeRequest request) {
        EmployeeEntity e = new EmployeeEntity();
        e.setFullName(request.getFullName());
        e.setTitle(request.getTitle());
        e.setSeniority(request.getSeniority());
        e.setYearsExperience(request.getYearsExperience());
        e.setPerformanceScore(request.getPerformanceScore());
        e.setAvailabilityState(request.getAvailabilityState());
        e.setCapacityHoursPerWeek(request.getCapacityHoursPerWeek());
        e.setProfileText(request.getProfileText());
        return toResponse(repository.save(e));
    }

    @Override
    @Transactional(readOnly = true)
    public EmployeeResponse get(String id) {
        return repository.findById(id).map(this::toResponse)
                .orElseThrow(() -> new EmployeeNotFoundException(id));
    }

    @Override
    public EmployeeResponse update(UpdateEmployeeRequest request) {
        EmployeeEntity e = repository.findById(request.getId())
                .orElseThrow(() -> new EmployeeNotFoundException(request.getId()));
        if (request.getFullName() != null) e.setFullName(request.getFullName());
        if (request.getTitle() != null) e.setTitle(request.getTitle());
        if (request.getSeniority() != null) e.setSeniority(request.getSeniority());
        if (request.getYearsExperience() != null) e.setYearsExperience(request.getYearsExperience());
        if (request.getPerformanceScore() != null) e.setPerformanceScore(request.getPerformanceScore());
        if (request.getAvailabilityState() != null) e.setAvailabilityState(request.getAvailabilityState());
        if (request.getCapacityHoursPerWeek() != null) e.setCapacityHoursPerWeek(request.getCapacityHoursPerWeek());
        if (request.getProfileText() != null) e.setProfileText(request.getProfileText());
        return toResponse(repository.save(e));
    }

    @Override
    public void delete(String id) {
        if (!repository.existsById(id)) {
            throw new EmployeeNotFoundException(id);
        }
        repository.deleteById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public PageResponse<EmployeeResponse> list(ListEmployeesRequest request) {
        int page = Math.max(request.getPage(), 1);
        Pageable pageable = PageRequest.of(page - 1, request.getPageSize(),
                Sort.by(Sort.Direction.DESC, "createdAt"));
        String search = request.getSearch();

        Page<EmployeeEntity> result = (search == null || search.isBlank())
                ? repository.findAll(pageable)
                : repository.findByFullNameContainingIgnoreCaseOrTitleContainingIgnoreCase(
                        search, search, pageable);

        List<EmployeeResponse> items = result.getContent().stream().map(this::toResponse).toList();
        return PageResponse.<EmployeeResponse>builder()
                .items(items)
                .page(page)
                .pageSize(request.getPageSize())
                .total(result.getTotalElements())
                .pages(result.getTotalPages())
                .build();
    }

    private EmployeeResponse toResponse(EmployeeEntity e) {
        return EmployeeResponse.builder()
                .id(e.getId())
                .fullName(e.getFullName())
                .title(e.getTitle())
                .seniority(e.getSeniority())
                .yearsExperience(e.getYearsExperience())
                .performanceScore(e.getPerformanceScore())
                .availabilityState(e.getAvailabilityState())
                .capacityHoursPerWeek(e.getCapacityHoursPerWeek())
                .profileText(e.getProfileText())
                .createdAt(e.getCreatedAt())
                .build();
    }
}
