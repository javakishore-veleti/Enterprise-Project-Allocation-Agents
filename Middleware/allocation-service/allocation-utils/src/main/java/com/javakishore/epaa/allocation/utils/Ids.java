package com.javakishore.epaa.allocation.utils;

import java.util.UUID;

/** UUID-as-String id helpers. */
public final class Ids {
    private Ids() {
    }

    public static String newId() {
        return UUID.randomUUID().toString();
    }
}
