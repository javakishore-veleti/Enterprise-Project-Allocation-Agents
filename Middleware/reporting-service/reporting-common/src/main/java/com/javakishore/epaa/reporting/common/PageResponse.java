package com.javakishore.epaa.reporting.common;

import java.util.List;
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
public class PageResponse<T> extends BaseResponse {
    private List<T> items;
    private int page;
    private int pageSize;
    private long total;
    private int pages;
}
