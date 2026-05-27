package com.javakishore.epaa.employee.utils;

import java.util.Set;

/** Canonical employee availability states (mirrors the paper / synthetic data). */
public final class AvailabilityStates {
    public static final String AVAILABLE = "available";
    public static final String PARTIALLY_OCCUPIED = "partially_occupied";
    public static final String UNAVAILABLE = "unavailable";

    public static final Set<String> ALL = Set.of(AVAILABLE, PARTIALLY_OCCUPIED, UNAVAILABLE);

    private AvailabilityStates() {
    }

    public static boolean isValid(String value) {
        return value != null && ALL.contains(value);
    }
}
