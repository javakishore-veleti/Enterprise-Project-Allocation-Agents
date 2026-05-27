package com.javakishore.epaa.employee.utils;

import java.util.UUID;

/** UUID-as-String id helpers (PK convention). */
public final class Ids {
    private Ids() {
    }

    public static String newId() {
        return UUID.randomUUID().toString();
    }
}
