package org.galaxyproject.gxformat2;

import java.util.ArrayList;
import java.util.List;

public class LintContext {
  private boolean foundErrors = false;
  private boolean foundWarns = false;

  private List<String> validMessages = new ArrayList<String>();
  private List<String> infoMessages = new ArrayList<String>();
  private List<String> warnMessages = new ArrayList<String>();
  private List<String> errorMessages = new ArrayList<String>();

  LintContext() {}

  public boolean getFoundErrors() {
    return this.foundErrors;
  }

  public boolean getFoundWarns() {
    return this.foundWarns;
  }

  void valid(String message, Object... args) {
    this.validMessages.add(String.format(message, args));
  }

  void info(String message, Object... args) {
    this.infoMessages.add(String.format(message, args));
  }

  void error(String message, Object... args) {
    this.foundErrors = true;
    this.errorMessages.add(String.format(message, args));
  }

  void warn(String message, Object... args) {
    this.foundWarns = true;
    this.warnMessages.add(String.format(message, args));
  }

  public List<String> collectMessages() {
    final List<String> messages = new ArrayList<String>();
    for (final String message : this.errorMessages) {
      messages.add(".. ERROR " + message);
    }

    for (final String message : this.warnMessages) {
      messages.add(".. WARNING " + message);
    }
    return messages;
  }

  public void printMessages() {
    for (final String message : this.collectMessages()) {
      System.out.println(message);
    }
  }
}
