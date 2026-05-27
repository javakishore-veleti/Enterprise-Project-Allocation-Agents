package com.javakishore.epaa.employee.services.dto;

import com.javakishore.epaa.employee.common.BaseRequest;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class UpdateEmployeeRequest extends BaseRequest {

    @NotBlank
    private String id;

    private String fullName;
    private String title;
    private String seniority;
    private Integer yearsExperience;
    private Double performanceScore;
    private String availabilityState;
    private Integer capacityHoursPerWeek;
    private String profileText;
}
