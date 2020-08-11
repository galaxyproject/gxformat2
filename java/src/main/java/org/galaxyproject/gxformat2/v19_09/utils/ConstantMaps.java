package org.galaxyproject.gxformat2.v19_09.utils;

import java.util.HashMap;

public class ConstantMaps {
  // declare as HashMap for clone().
  public static final HashMap<String, String> vocab = new HashMap();
  public static final HashMap<String, String> rvocab = new HashMap();

  static {
    vocab.put("Any", "https://w3id.org/cwl/salad#Any");
    vocab.put("ArraySchema", "https://w3id.org/cwl/salad#ArraySchema");
    vocab.put("Documented", "https://w3id.org/cwl/salad#Documented");
    vocab.put("EnumSchema", "https://w3id.org/cwl/salad#EnumSchema");
    vocab.put("File", "https://galaxyproject.org/gxformat2/v19_09#GalaxyType/File");
    vocab.put("GalaxyType", "https://galaxyproject.org/gxformat2/v19_09#GalaxyType");
    vocab.put("GalaxyWorkflow", "https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow");
    vocab.put("HasStepErrors", "https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors");
    vocab.put(
        "HasStepPosition", "https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition");
    vocab.put("HasUUID", "https://galaxyproject.org/gxformat2/gxformat2common#HasUUID");
    vocab.put("Identified", "https://w3id.org/cwl/cwl#Identified");
    vocab.put("InputParameter", "https://w3id.org/cwl/cwl#InputParameter");
    vocab.put("Labeled", "https://w3id.org/cwl/cwl#Labeled");
    vocab.put("OutputParameter", "https://w3id.org/cwl/cwl#OutputParameter");
    vocab.put("Parameter", "https://w3id.org/cwl/cwl#Parameter");
    vocab.put("PrimitiveType", "https://w3id.org/cwl/salad#PrimitiveType");
    vocab.put("Process", "https://w3id.org/cwl/cwl#Process");
    vocab.put("RecordField", "https://w3id.org/cwl/salad#RecordField");
    vocab.put("RecordSchema", "https://w3id.org/cwl/salad#RecordSchema");
    vocab.put(
        "ReferencesTool", "https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool");
    vocab.put("Report", "https://galaxyproject.org/gxformat2/v19_09#Report");
    vocab.put("Sink", "https://galaxyproject.org/gxformat2/v19_09#Sink");
    vocab.put("StepPosition", "https://galaxyproject.org/gxformat2/gxformat2common#StepPosition");
    vocab.put(
        "ToolShedRepository",
        "https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository");
    vocab.put(
        "WorkflowInputParameter",
        "https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter");
    vocab.put(
        "WorkflowOutputParameter",
        "https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter");
    vocab.put("WorkflowStep", "https://galaxyproject.org/gxformat2/v19_09#WorkflowStep");
    vocab.put("WorkflowStepInput", "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepInput");
    vocab.put(
        "WorkflowStepOutput", "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput");
    vocab.put("WorkflowStepType", "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType");
    vocab.put("array", "array");
    vocab.put("boolean", "http://www.w3.org/2001/XMLSchema#boolean");
    vocab.put("collection", "https://galaxyproject.org/gxformat2/v19_09#GalaxyType/collection");
    vocab.put("data", "https://galaxyproject.org/gxformat2/v19_09#GalaxyType/data");
    vocab.put("double", "http://www.w3.org/2001/XMLSchema#double");
    vocab.put("enum", "enum");
    vocab.put("float", "http://www.w3.org/2001/XMLSchema#float");
    vocab.put("int", "http://www.w3.org/2001/XMLSchema#int");
    vocab.put("integer", "https://galaxyproject.org/gxformat2/v19_09#GalaxyType/integer");
    vocab.put("long", "http://www.w3.org/2001/XMLSchema#long");
    vocab.put("null", "https://w3id.org/cwl/salad#null");
    vocab.put("pause", "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType/pause");
    vocab.put("record", "record");
    vocab.put("string", "http://www.w3.org/2001/XMLSchema#string");
    vocab.put(
        "subworkflow", "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType/subworkflow");
    vocab.put("text", "https://galaxyproject.org/gxformat2/v19_09#GalaxyType/text");
    vocab.put("tool", "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType/tool");

    rvocab.put("https://w3id.org/cwl/salad#Any", "Any");
    rvocab.put("https://w3id.org/cwl/salad#ArraySchema", "ArraySchema");
    rvocab.put("https://w3id.org/cwl/salad#Documented", "Documented");
    rvocab.put("https://w3id.org/cwl/salad#EnumSchema", "EnumSchema");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#GalaxyType/File", "File");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#GalaxyType", "GalaxyType");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow", "GalaxyWorkflow");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors", "HasStepErrors");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition", "HasStepPosition");
    rvocab.put("https://galaxyproject.org/gxformat2/gxformat2common#HasUUID", "HasUUID");
    rvocab.put("https://w3id.org/cwl/cwl#Identified", "Identified");
    rvocab.put("https://w3id.org/cwl/cwl#InputParameter", "InputParameter");
    rvocab.put("https://w3id.org/cwl/cwl#Labeled", "Labeled");
    rvocab.put("https://w3id.org/cwl/cwl#OutputParameter", "OutputParameter");
    rvocab.put("https://w3id.org/cwl/cwl#Parameter", "Parameter");
    rvocab.put("https://w3id.org/cwl/salad#PrimitiveType", "PrimitiveType");
    rvocab.put("https://w3id.org/cwl/cwl#Process", "Process");
    rvocab.put("https://w3id.org/cwl/salad#RecordField", "RecordField");
    rvocab.put("https://w3id.org/cwl/salad#RecordSchema", "RecordSchema");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool", "ReferencesTool");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#Report", "Report");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#Sink", "Sink");
    rvocab.put("https://galaxyproject.org/gxformat2/gxformat2common#StepPosition", "StepPosition");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository",
        "ToolShedRepository");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter",
        "WorkflowInputParameter");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter",
        "WorkflowOutputParameter");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#WorkflowStep", "WorkflowStep");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#WorkflowStepInput", "WorkflowStepInput");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput", "WorkflowStepOutput");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType", "WorkflowStepType");
    rvocab.put("array", "array");
    rvocab.put("http://www.w3.org/2001/XMLSchema#boolean", "boolean");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#GalaxyType/collection", "collection");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#GalaxyType/data", "data");
    rvocab.put("http://www.w3.org/2001/XMLSchema#double", "double");
    rvocab.put("enum", "enum");
    rvocab.put("http://www.w3.org/2001/XMLSchema#float", "float");
    rvocab.put("http://www.w3.org/2001/XMLSchema#int", "int");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#GalaxyType/integer", "integer");
    rvocab.put("http://www.w3.org/2001/XMLSchema#long", "long");
    rvocab.put("https://w3id.org/cwl/salad#null", "null");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType/pause", "pause");
    rvocab.put("record", "record");
    rvocab.put("http://www.w3.org/2001/XMLSchema#string", "string");
    rvocab.put(
        "https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType/subworkflow", "subworkflow");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#GalaxyType/text", "text");
    rvocab.put("https://galaxyproject.org/gxformat2/v19_09#WorkflowStepType/tool", "tool");
  }
}
