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

  boolean getFoundErrors() {
    return this.foundErrors;
  }

  boolean getFoundWarns() {
    return this.foundWarns;
  }

  void valid(String message, Object... args) {
    this.validMessages.add(String.format(message, args));
  }

  void info(String message, Object... args) {
    this.infoMessages.add(String.format(message, args));
  }

  void error(String message, Object... args) {
    this.errorMessages.add(String.format(message, args));
  }

  void warn(String message, Object... args) {
    this.warnMessages.add(String.format(message, args));
  }

  void printMessages() {
    for (final String message : this.errorMessages) {
      this.foundErrors = true;
      System.out.print(".. ERROR " + message);
    }

    for (final String message : this.warnMessages) {
      this.foundWarns = true;
      System.out.print(".. WARNING " + message);
    }
  }
}
