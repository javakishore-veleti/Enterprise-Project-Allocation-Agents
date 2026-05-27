package com.javakishore.epaa.employee.services.dto;

import com.javakishore.epaa.employee.common.BaseResponse;
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
public class EmployeeResponse extends BaseResponse {
    private String id;
    private String fullName;
    private String title;
    private String seniority;
    private Integer yearsExperience;
    private Double performanceScore;
    private String availabilityState;
    private Integer capacityHoursPerWeek;
    private String profileText;
    private OffsetDateTime createdAt;
}
