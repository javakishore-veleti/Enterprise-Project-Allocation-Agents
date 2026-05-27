package com.javakishore.epaa.project.services.dto;

import com.javakishore.epaa.project.common.BaseResponse;
import java.time.LocalDate;
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
public class ProjectResponse extends BaseResponse {
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
    private OffsetDateTime createdAt;
}
