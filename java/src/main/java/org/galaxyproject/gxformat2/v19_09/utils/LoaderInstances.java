package org.galaxyproject.gxformat2.v19_09.utils;

import org.galaxyproject.gxformat2.v19_09.*;

public class LoaderInstances {
  public static Loader<String> StringInstance = new PrimitiveLoader<String>(String.class);
  public static Loader<Integer> IntegerInstance = new PrimitiveLoader<Integer>(Integer.class);
  public static Loader<Long> LongInstance = new PrimitiveLoader<Long>(Long.class);
  public static Loader<Double> DoubleInstance = new PrimitiveLoader<Double>(Double.class);
  public static Loader<Boolean> BooleanInstance = new PrimitiveLoader<Boolean>(Boolean.class);
  public static Loader<Object> NullInstance = new NullLoader();
  public static Loader<Object> AnyInstance = new AnyLoader();
  public static Loader<org.galaxyproject.gxformat2.v19_09.Documented> Documented =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.Documented>(
          org.galaxyproject.gxformat2.v19_09.Documented.class);
  public static Loader<PrimitiveType> PrimitiveType = new EnumLoader(PrimitiveType.class);
  public static Loader<Any> Any = new EnumLoader(Any.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.RecordField> RecordField =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.RecordField>(
          org.galaxyproject.gxformat2.v19_09.RecordFieldImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.RecordSchema> RecordSchema =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.RecordSchema>(
          org.galaxyproject.gxformat2.v19_09.RecordSchemaImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.EnumSchema> EnumSchema =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.EnumSchema>(
          org.galaxyproject.gxformat2.v19_09.EnumSchemaImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.ArraySchema> ArraySchema =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.ArraySchema>(
          org.galaxyproject.gxformat2.v19_09.ArraySchemaImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.Labeled> Labeled =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.Labeled>(
          org.galaxyproject.gxformat2.v19_09.Labeled.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.Identified> Identified =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.Identified>(
          org.galaxyproject.gxformat2.v19_09.Identified.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.Parameter> Parameter =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.Parameter>(
          org.galaxyproject.gxformat2.v19_09.Parameter.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.InputParameter> InputParameter =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.InputParameter>(
          org.galaxyproject.gxformat2.v19_09.InputParameter.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.OutputParameter> OutputParameter =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.OutputParameter>(
          org.galaxyproject.gxformat2.v19_09.OutputParameter.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.Process> Process =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.Process>(
          org.galaxyproject.gxformat2.v19_09.Process.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.HasUUID> HasUUID =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.HasUUID>(
          org.galaxyproject.gxformat2.v19_09.HasUUID.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.HasStepErrors> HasStepErrors =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.HasStepErrors>(
          org.galaxyproject.gxformat2.v19_09.HasStepErrors.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.HasStepPosition> HasStepPosition =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.HasStepPosition>(
          org.galaxyproject.gxformat2.v19_09.HasStepPosition.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.StepPosition> StepPosition =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.StepPosition>(
          org.galaxyproject.gxformat2.v19_09.StepPositionImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.ReferencesTool> ReferencesTool =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.ReferencesTool>(
          org.galaxyproject.gxformat2.v19_09.ReferencesTool.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.ToolShedRepository> ToolShedRepository =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.ToolShedRepository>(
          org.galaxyproject.gxformat2.v19_09.ToolShedRepositoryImpl.class);
  public static Loader<GalaxyType> GalaxyType = new EnumLoader(GalaxyType.class);
  public static Loader<WorkflowStepType> WorkflowStepType = new EnumLoader(WorkflowStepType.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.WorkflowInputParameter>
      WorkflowInputParameter =
          new RecordLoader<org.galaxyproject.gxformat2.v19_09.WorkflowInputParameter>(
              org.galaxyproject.gxformat2.v19_09.WorkflowInputParameterImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.WorkflowOutputParameter>
      WorkflowOutputParameter =
          new RecordLoader<org.galaxyproject.gxformat2.v19_09.WorkflowOutputParameter>(
              org.galaxyproject.gxformat2.v19_09.WorkflowOutputParameterImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.WorkflowStep> WorkflowStep =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.WorkflowStep>(
          org.galaxyproject.gxformat2.v19_09.WorkflowStepImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.Sink> Sink =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.Sink>(
          org.galaxyproject.gxformat2.v19_09.Sink.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.WorkflowStepInput> WorkflowStepInput =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.WorkflowStepInput>(
          org.galaxyproject.gxformat2.v19_09.WorkflowStepInputImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.Report> Report =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.Report>(
          org.galaxyproject.gxformat2.v19_09.ReportImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.WorkflowStepOutput> WorkflowStepOutput =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.WorkflowStepOutput>(
          org.galaxyproject.gxformat2.v19_09.WorkflowStepOutputImpl.class);
  public static Loader<org.galaxyproject.gxformat2.v19_09.GalaxyWorkflow> GalaxyWorkflow =
      new RecordLoader<org.galaxyproject.gxformat2.v19_09.GalaxyWorkflow>(
          org.galaxyproject.gxformat2.v19_09.GalaxyWorkflowImpl.class);
  public static Loader<java.util.List<String>> array_of_StringInstance =
      new ArrayLoader(StringInstance);
  public static Loader<Object> union_of_NullInstance_or_StringInstance_or_array_of_StringInstance =
      new UnionLoader(new Loader[] {NullInstance, StringInstance, array_of_StringInstance});
  public static Loader<String> uri_StringInstance_True_False_None =
      new UriLoader(StringInstance, true, false, null);
  public static Loader<Object>
      union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance =
          new UnionLoader(
              new Loader[] {PrimitiveType, RecordSchema, EnumSchema, ArraySchema, StringInstance});
  public static Loader<java.util.List<Object>>
      array_of_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance =
          new ArrayLoader(
              union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance);
  public static Loader<Object>
      union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance_or_array_of_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance =
          new UnionLoader(
              new Loader[] {
                PrimitiveType,
                RecordSchema,
                EnumSchema,
                ArraySchema,
                StringInstance,
                array_of_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance
              });
  public static Loader<Object>
      typedsl_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance_or_array_of_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance_2 =
          new TypeDslLoader(
              union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance_or_array_of_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance,
              2);
  public static Loader<java.util.List<RecordField>> array_of_RecordField =
      new ArrayLoader(RecordField);
  public static Loader<java.util.Optional<java.util.List<Object>>> optional_array_of_RecordField =
      new OptionalLoader(array_of_RecordField);
  public static Loader<java.util.Optional<java.util.List<Object>>>
      idmap_fields_optional_array_of_RecordField =
          new IdMapLoader(optional_array_of_RecordField, "name", "type");
  public static Loader<enum_d9cba076fca539106791a4f46d198c7fcfbdb779>
      enum_d9cba076fca539106791a4f46d198c7fcfbdb779 =
          new EnumLoader(enum_d9cba076fca539106791a4f46d198c7fcfbdb779.class);
  public static Loader<enum_d9cba076fca539106791a4f46d198c7fcfbdb779>
      typedsl_enum_d9cba076fca539106791a4f46d198c7fcfbdb779_2 =
          new TypeDslLoader(enum_d9cba076fca539106791a4f46d198c7fcfbdb779, 2);
  public static Loader<java.util.List<String>> uri_array_of_StringInstance_True_False_None =
      new UriLoader(array_of_StringInstance, true, false, null);
  public static Loader<enum_d961d79c225752b9fadb617367615ab176b47d77>
      enum_d961d79c225752b9fadb617367615ab176b47d77 =
          new EnumLoader(enum_d961d79c225752b9fadb617367615ab176b47d77.class);
  public static Loader<enum_d961d79c225752b9fadb617367615ab176b47d77>
      typedsl_enum_d961d79c225752b9fadb617367615ab176b47d77_2 =
          new TypeDslLoader(enum_d961d79c225752b9fadb617367615ab176b47d77, 2);
  public static Loader<Object>
      uri_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance_or_array_of_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance_False_True_2 =
          new UriLoader(
              union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance_or_array_of_union_of_PrimitiveType_or_RecordSchema_or_EnumSchema_or_ArraySchema_or_StringInstance,
              false,
              true,
              2);
  public static Loader<enum_d062602be0b4b8fd33e69e29a841317b6ab665bc>
      enum_d062602be0b4b8fd33e69e29a841317b6ab665bc =
          new EnumLoader(enum_d062602be0b4b8fd33e69e29a841317b6ab665bc.class);
  public static Loader<enum_d062602be0b4b8fd33e69e29a841317b6ab665bc>
      typedsl_enum_d062602be0b4b8fd33e69e29a841317b6ab665bc_2 =
          new TypeDslLoader(enum_d062602be0b4b8fd33e69e29a841317b6ab665bc, 2);
  public static Loader<java.util.Optional<String>> optional_StringInstance =
      new OptionalLoader(StringInstance);
  public static Loader<java.util.Optional<String>> uri_optional_StringInstance_True_False_None =
      new UriLoader(optional_StringInstance, true, false, null);
  public static Loader<java.util.Optional<Object>> optional_AnyInstance =
      new OptionalLoader(AnyInstance);
  public static Loader<java.util.List<WorkflowInputParameter>> array_of_WorkflowInputParameter =
      new ArrayLoader(WorkflowInputParameter);
  public static Loader<java.util.List<Object>> idmap_inputs_array_of_WorkflowInputParameter =
      new IdMapLoader(array_of_WorkflowInputParameter, "id", "type");
  public static Loader<java.util.List<WorkflowOutputParameter>> array_of_WorkflowOutputParameter =
      new ArrayLoader(WorkflowOutputParameter);
  public static Loader<java.util.List<Object>> idmap_outputs_array_of_WorkflowOutputParameter =
      new IdMapLoader(array_of_WorkflowOutputParameter, "id", "type");
  public static Loader<java.util.Optional<StepPosition>> optional_StepPosition =
      new OptionalLoader(StepPosition);
  public static Loader<Object> union_of_DoubleInstance_or_IntegerInstance =
      new UnionLoader(new Loader[] {DoubleInstance, IntegerInstance});
  public static Loader<java.util.Optional<ToolShedRepository>> optional_ToolShedRepository =
      new OptionalLoader(ToolShedRepository);
  public static Loader<Object> union_of_GalaxyType_or_StringInstance_or_NullInstance =
      new UnionLoader(new Loader[] {GalaxyType, StringInstance, NullInstance});
  public static Loader<Object> typedsl_union_of_GalaxyType_or_StringInstance_or_NullInstance_2 =
      new TypeDslLoader(union_of_GalaxyType_or_StringInstance_or_NullInstance, 2);
  public static Loader<java.util.Optional<Boolean>> optional_BooleanInstance =
      new OptionalLoader(BooleanInstance);
  public static Loader<java.util.Optional<java.util.List<String>>>
      optional_array_of_StringInstance = new OptionalLoader(array_of_StringInstance);
  public static Loader<java.util.Optional<GalaxyType>> optional_GalaxyType =
      new OptionalLoader(GalaxyType);
  public static Loader<java.util.Optional<GalaxyType>> typedsl_optional_GalaxyType_2 =
      new TypeDslLoader(optional_GalaxyType, 2);
  public static Loader<java.util.List<WorkflowStepInput>> array_of_WorkflowStepInput =
      new ArrayLoader(WorkflowStepInput);
  public static Loader<java.util.Optional<java.util.List<Object>>>
      optional_array_of_WorkflowStepInput = new OptionalLoader(array_of_WorkflowStepInput);
  public static Loader<java.util.Optional<java.util.List<Object>>>
      idmap_in_optional_array_of_WorkflowStepInput =
          new IdMapLoader(optional_array_of_WorkflowStepInput, "id", "source");
  public static Loader<Object> union_of_StringInstance_or_WorkflowStepOutput =
      new UnionLoader(new Loader[] {StringInstance, WorkflowStepOutput});
  public static Loader<java.util.List<Object>>
      array_of_union_of_StringInstance_or_WorkflowStepOutput =
          new ArrayLoader(union_of_StringInstance_or_WorkflowStepOutput);
  public static Loader<java.util.Optional<java.util.List<Object>>>
      optional_array_of_union_of_StringInstance_or_WorkflowStepOutput =
          new OptionalLoader(array_of_union_of_StringInstance_or_WorkflowStepOutput);
  public static Loader<java.util.Optional<java.util.List<Object>>>
      idmap_out_optional_array_of_union_of_StringInstance_or_WorkflowStepOutput =
          new IdMapLoader(
              optional_array_of_union_of_StringInstance_or_WorkflowStepOutput, "id", "source");
  public static Loader<java.util.Optional<WorkflowStepType>> optional_WorkflowStepType =
      new OptionalLoader(WorkflowStepType);
  public static Loader<java.util.Optional<WorkflowStepType>> typedsl_optional_WorkflowStepType_2 =
      new TypeDslLoader(optional_WorkflowStepType, 2);
  public static Loader<java.util.Optional<GalaxyWorkflow>> optional_GalaxyWorkflow =
      new OptionalLoader(GalaxyWorkflow);
  public static Loader<java.util.Optional<GalaxyWorkflow>>
      uri_optional_GalaxyWorkflow_False_False_None =
          new UriLoader(optional_GalaxyWorkflow, false, false, null);
  public static Loader<Object>
      uri_union_of_NullInstance_or_StringInstance_or_array_of_StringInstance_False_False_2 =
          new UriLoader(
              union_of_NullInstance_or_StringInstance_or_array_of_StringInstance, false, false, 2);
  public static Loader<String> uri_StringInstance_False_True_None =
      new UriLoader(StringInstance, false, true, null);
  public static Loader<java.util.List<WorkflowStep>> array_of_WorkflowStep =
      new ArrayLoader(WorkflowStep);
  public static Loader<java.util.List<Object>> idmap_steps_array_of_WorkflowStep =
      new IdMapLoader(array_of_WorkflowStep, "id", "None");
  public static Loader<java.util.Optional<Report>> optional_Report = new OptionalLoader(Report);
  public static Loader<java.util.List<GalaxyWorkflow>> array_of_GalaxyWorkflow =
      new ArrayLoader(GalaxyWorkflow);
  public static Loader<Object> union_of_GalaxyWorkflow_or_array_of_GalaxyWorkflow =
      new UnionLoader(new Loader[] {GalaxyWorkflow, array_of_GalaxyWorkflow});
}
