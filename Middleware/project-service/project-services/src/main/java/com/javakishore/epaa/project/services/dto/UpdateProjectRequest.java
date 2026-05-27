package com.javakishore.epaa.project.services.dto;

import com.javakishore.epaa.project.common.BaseRequest;
import jakarta.validation.constraints.NotBlank;
import java.time.LocalDate;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class UpdateProjectRequest extends BaseRequest {

    @NotBlank
    private String id;

    private String name;
    private String clientName;
    private String priority;
    private String complexity;
    private Integer durationWeeks;
    private Integer requiredHeadcount;
    private LocalDate startDate;
    private String status;
    private String briefText;
}
