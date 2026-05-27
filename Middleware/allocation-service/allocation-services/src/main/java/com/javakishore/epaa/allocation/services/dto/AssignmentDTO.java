package com.javakishore.epaa.allocation.services.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** One assigned team member (mirrors the Agents service response). */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AssignmentDTO {

    @JsonProperty("full_name")
    private String fullName;

    private Integer rank;

    @JsonProperty("final_score")
    private Double finalScore;
}
