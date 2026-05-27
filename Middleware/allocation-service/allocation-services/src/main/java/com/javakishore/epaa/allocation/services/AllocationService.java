package com.javakishore.epaa.allocation.services;

import com.javakishore.epaa.allocation.services.dto.AllocationRunResponse;
import com.javakishore.epaa.allocation.services.dto.RunAllocationRequest;

public interface AllocationService {

    /** Trigger the Agents pipeline for a project and record the request. */
    AllocationRunResponse run(RunAllocationRequest request);
}
