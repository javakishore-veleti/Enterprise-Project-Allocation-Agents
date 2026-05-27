package com.javakishore.epaa.allocation.api;

import com.javakishore.epaa.allocation.services.AllocationService;
import com.javakishore.epaa.allocation.services.dto.AllocationRunResponse;
import com.javakishore.epaa.allocation.services.dto.RunAllocationRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/allocations")
public class AllocationController {

    private final AllocationService service;

    public AllocationController(AllocationService service) {
        this.service = service;
    }

    /** Trigger the 6-agent allocation pipeline for a project. */
    @PostMapping("/run")
    public AllocationRunResponse run(@Valid @RequestBody RunAllocationRequest request) {
        return service.run(request);
    }
}
