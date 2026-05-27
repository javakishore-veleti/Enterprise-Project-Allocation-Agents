package com.javakishore.epaa.allocation.services.dto;

import com.javakishore.epaa.allocation.common.BaseRequest;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class RunAllocationRequest extends BaseRequest {

    @NotBlank
    private String projectId;
}
