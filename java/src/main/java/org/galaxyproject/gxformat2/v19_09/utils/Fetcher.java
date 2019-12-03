package org.galaxyproject.gxformat2.v19_09.utils;

public interface Fetcher {

  public abstract String urlJoin(final String baseUrl, final String url);

  public abstract String fetchText(final String url);
}
