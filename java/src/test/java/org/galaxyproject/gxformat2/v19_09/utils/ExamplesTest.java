package org.galaxyproject.gxformat2.v19_09.utils;

public class ExamplesTest {

  @org.junit.Test
  public void testvalid1ByString() throws Exception {
    java.net.URL url = getClass().getResource("valid1.yml");
    java.nio.file.Path resPath = java.nio.file.Paths.get(url.toURI());
    String yaml = new String(java.nio.file.Files.readAllBytes(resPath), "UTF8");
    RootLoader.loadDocument(yaml, url.toString());
  }

  @org.junit.Test
  public void testvalid1ByPath() throws Exception {
    java.net.URL url = getClass().getResource("valid1.yml");
    java.nio.file.Path resPath = java.nio.file.Paths.get(url.toURI());
    RootLoader.loadDocument(resPath);
  }

  @org.junit.Test
  public void testvalid1ByMap() throws Exception {
    java.net.URL url = getClass().getResource("valid1.yml");
    java.nio.file.Path resPath = java.nio.file.Paths.get(url.toURI());
    String yaml = new String(java.nio.file.Files.readAllBytes(resPath), "UTF8");
    java.util.Map<String, Object> doc;
    doc = (java.util.Map<String, Object>) YamlUtils.mapFromString(yaml);
    RootLoader.loadDocument(doc, url.toString());
  }
}
