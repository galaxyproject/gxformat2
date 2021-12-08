import {
  _AnyLoader,
  _ExpressionLoader,
  _PrimitiveLoader,
  _UnionLoader,
  _RecordLoader,
  _URILoader,
  _ArrayLoader,
  _EnumLoader,
  _IdMapLoader,
  _TypeDSLLoader,
  _SecondaryDSLLoader,
  TypeGuards,
  Any,
  ArraySchema,
  ArraySchemaProperties,
  DocumentedProperties,
  EnumSchema,
  EnumSchemaProperties,
  GalaxyType,
  GalaxyWorkflow,
  GalaxyWorkflowProperties,
  HasStepErrorsProperties,
  HasStepPositionProperties,
  HasUUIDProperties,
  IdentifiedProperties,
  InputParameterProperties,
  LabeledProperties,
  OutputParameterProperties,
  ParameterProperties,
  PrimitiveType,
  ProcessProperties,
  RecordField,
  RecordFieldProperties,
  RecordSchema,
  RecordSchemaProperties,
  ReferencesToolProperties,
  Report,
  ReportProperties,
  SinkProperties,
  StepPosition,
  StepPositionProperties,
  ToolShedRepository,
  ToolShedRepositoryProperties,
  WorkflowInputParameter,
  WorkflowInputParameterProperties,
  WorkflowOutputParameter,
  WorkflowOutputParameterProperties,
  WorkflowStep,
  WorkflowStepInput,
  WorkflowStepInputProperties,
  WorkflowStepOutput,
  WorkflowStepOutputProperties,
  WorkflowStepProperties,
  WorkflowStepType,
  enum_d062602be0b4b8fd33e69e29a841317b6ab665bc,
  enum_d961d79c225752b9fadb617367615ab176b47d77,
  enum_d9cba076fca539106791a4f46d198c7fcfbdb779
} from './Internal'

export const strtype = new _PrimitiveLoader(TypeGuards.String);
export const inttype = new _PrimitiveLoader(TypeGuards.Int);
export const floattype = new _PrimitiveLoader(TypeGuards.Float);
export const booltype = new _PrimitiveLoader(TypeGuards.Bool);
export const undefinedtype = new _PrimitiveLoader(TypeGuards.Undefined);
export const anyType = new _AnyLoader();
export const PrimitiveTypeLoader = new _EnumLoader((Object.keys(PrimitiveType) as Array<keyof typeof PrimitiveType>).map(key => PrimitiveType[key]));
export const AnyLoader = new _EnumLoader((Object.keys(Any) as Array<keyof typeof Any>).map(key => Any[key]));
export const RecordFieldLoader = new _RecordLoader(RecordField.fromDoc);
export const RecordSchemaLoader = new _RecordLoader(RecordSchema.fromDoc);
export const EnumSchemaLoader = new _RecordLoader(EnumSchema.fromDoc);
export const ArraySchemaLoader = new _RecordLoader(ArraySchema.fromDoc);
export const StepPositionLoader = new _RecordLoader(StepPosition.fromDoc);
export const ToolShedRepositoryLoader = new _RecordLoader(ToolShedRepository.fromDoc);
export const GalaxyTypeLoader = new _EnumLoader((Object.keys(GalaxyType) as Array<keyof typeof GalaxyType>).map(key => GalaxyType[key]));
export const WorkflowStepTypeLoader = new _EnumLoader((Object.keys(WorkflowStepType) as Array<keyof typeof WorkflowStepType>).map(key => WorkflowStepType[key]));
export const WorkflowInputParameterLoader = new _RecordLoader(WorkflowInputParameter.fromDoc);
export const WorkflowOutputParameterLoader = new _RecordLoader(WorkflowOutputParameter.fromDoc);
export const WorkflowStepLoader = new _RecordLoader(WorkflowStep.fromDoc);
export const WorkflowStepInputLoader = new _RecordLoader(WorkflowStepInput.fromDoc);
export const ReportLoader = new _RecordLoader(Report.fromDoc);
export const WorkflowStepOutputLoader = new _RecordLoader(WorkflowStepOutput.fromDoc);
export const GalaxyWorkflowLoader = new _RecordLoader(GalaxyWorkflow.fromDoc);
export const arrayOfstrtype = new _ArrayLoader([strtype]);
export const unionOfundefinedtypeOrstrtypeOrarrayOfstrtype = new _UnionLoader([undefinedtype, strtype, arrayOfstrtype]);
export const uristrtypeTrueFalseNone = new _URILoader(strtype, true, false, undefined);
export const unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype = new _UnionLoader([PrimitiveTypeLoader, RecordSchemaLoader, EnumSchemaLoader, ArraySchemaLoader, strtype]);
export const arrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype = new _ArrayLoader([unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype]);
export const unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype = new _UnionLoader([PrimitiveTypeLoader, RecordSchemaLoader, EnumSchemaLoader, ArraySchemaLoader, strtype, arrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype]);
export const typedslunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype2 = new _TypeDSLLoader(unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype, 2);
export const arrayOfRecordFieldLoader = new _ArrayLoader([RecordFieldLoader]);
export const unionOfundefinedtypeOrarrayOfRecordFieldLoader = new _UnionLoader([undefinedtype, arrayOfRecordFieldLoader]);
export const idmapfieldsunionOfundefinedtypeOrarrayOfRecordFieldLoader = new _IdMapLoader(unionOfundefinedtypeOrarrayOfRecordFieldLoader, 'name', 'type');
export const enum_d9cba076fca539106791a4f46d198c7fcfbdb779Loader = new _EnumLoader((Object.keys(enum_d9cba076fca539106791a4f46d198c7fcfbdb779) as Array<keyof typeof enum_d9cba076fca539106791a4f46d198c7fcfbdb779>).map(key => enum_d9cba076fca539106791a4f46d198c7fcfbdb779[key]));
export const typedslenum_d9cba076fca539106791a4f46d198c7fcfbdb779Loader2 = new _TypeDSLLoader(enum_d9cba076fca539106791a4f46d198c7fcfbdb779Loader, 2);
export const uriarrayOfstrtypeTrueFalseNone = new _URILoader(arrayOfstrtype, true, false, undefined);
export const enum_d961d79c225752b9fadb617367615ab176b47d77Loader = new _EnumLoader((Object.keys(enum_d961d79c225752b9fadb617367615ab176b47d77) as Array<keyof typeof enum_d961d79c225752b9fadb617367615ab176b47d77>).map(key => enum_d961d79c225752b9fadb617367615ab176b47d77[key]));
export const typedslenum_d961d79c225752b9fadb617367615ab176b47d77Loader2 = new _TypeDSLLoader(enum_d961d79c225752b9fadb617367615ab176b47d77Loader, 2);
export const uriunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeFalseTrue2 = new _URILoader(unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype, false, true, 2);
export const enum_d062602be0b4b8fd33e69e29a841317b6ab665bcLoader = new _EnumLoader((Object.keys(enum_d062602be0b4b8fd33e69e29a841317b6ab665bc) as Array<keyof typeof enum_d062602be0b4b8fd33e69e29a841317b6ab665bc>).map(key => enum_d062602be0b4b8fd33e69e29a841317b6ab665bc[key]));
export const typedslenum_d062602be0b4b8fd33e69e29a841317b6ab665bcLoader2 = new _TypeDSLLoader(enum_d062602be0b4b8fd33e69e29a841317b6ab665bcLoader, 2);
export const unionOfundefinedtypeOrstrtype = new _UnionLoader([undefinedtype, strtype]);
export const uriunionOfundefinedtypeOrstrtypeTrueFalseNone = new _URILoader(unionOfundefinedtypeOrstrtype, true, false, undefined);
export const unionOfundefinedtypeOranyType = new _UnionLoader([undefinedtype, anyType]);
export const unionOfWorkflowInputParameterLoader = new _UnionLoader([WorkflowInputParameterLoader]);
export const arrayOfunionOfWorkflowInputParameterLoader = new _ArrayLoader([unionOfWorkflowInputParameterLoader]);
export const idmapinputsarrayOfunionOfWorkflowInputParameterLoader = new _IdMapLoader(arrayOfunionOfWorkflowInputParameterLoader, 'id', 'type');
export const unionOfWorkflowOutputParameterLoader = new _UnionLoader([WorkflowOutputParameterLoader]);
export const arrayOfunionOfWorkflowOutputParameterLoader = new _ArrayLoader([unionOfWorkflowOutputParameterLoader]);
export const idmapoutputsarrayOfunionOfWorkflowOutputParameterLoader = new _IdMapLoader(arrayOfunionOfWorkflowOutputParameterLoader, 'id', 'type');
export const unionOfundefinedtypeOrStepPositionLoader = new _UnionLoader([undefinedtype, StepPositionLoader]);
export const unionOffloattypeOrinttype = new _UnionLoader([floattype, inttype]);
export const unionOfundefinedtypeOrToolShedRepositoryLoader = new _UnionLoader([undefinedtype, ToolShedRepositoryLoader]);
export const unionOfGalaxyTypeLoaderOrstrtypeOrundefinedtype = new _UnionLoader([GalaxyTypeLoader, strtype, undefinedtype]);
export const typedslunionOfGalaxyTypeLoaderOrstrtypeOrundefinedtype2 = new _TypeDSLLoader(unionOfGalaxyTypeLoaderOrstrtypeOrundefinedtype, 2);
export const unionOfbooltypeOrundefinedtype = new _UnionLoader([booltype, undefinedtype]);
export const unionOfundefinedtypeOrarrayOfstrtype = new _UnionLoader([undefinedtype, arrayOfstrtype]);
export const unionOfundefinedtypeOrGalaxyTypeLoader = new _UnionLoader([undefinedtype, GalaxyTypeLoader]);
export const typedslunionOfundefinedtypeOrGalaxyTypeLoader2 = new _TypeDSLLoader(unionOfundefinedtypeOrGalaxyTypeLoader, 2);
export const arrayOfWorkflowStepInputLoader = new _ArrayLoader([WorkflowStepInputLoader]);
export const unionOfundefinedtypeOrarrayOfWorkflowStepInputLoader = new _UnionLoader([undefinedtype, arrayOfWorkflowStepInputLoader]);
export const idmapin_unionOfundefinedtypeOrarrayOfWorkflowStepInputLoader = new _IdMapLoader(unionOfundefinedtypeOrarrayOfWorkflowStepInputLoader, 'id', 'source');
export const unionOfstrtypeOrWorkflowStepOutputLoader = new _UnionLoader([strtype, WorkflowStepOutputLoader]);
export const arrayOfunionOfstrtypeOrWorkflowStepOutputLoader = new _ArrayLoader([unionOfstrtypeOrWorkflowStepOutputLoader]);
export const unionOfarrayOfunionOfstrtypeOrWorkflowStepOutputLoaderOrundefinedtype = new _UnionLoader([arrayOfunionOfstrtypeOrWorkflowStepOutputLoader, undefinedtype]);
export const idmapoutunionOfarrayOfunionOfstrtypeOrWorkflowStepOutputLoaderOrundefinedtype = new _IdMapLoader(unionOfarrayOfunionOfstrtypeOrWorkflowStepOutputLoaderOrundefinedtype, 'id', 'source');
export const unionOfundefinedtypeOrWorkflowStepTypeLoader = new _UnionLoader([undefinedtype, WorkflowStepTypeLoader]);
export const typedslunionOfundefinedtypeOrWorkflowStepTypeLoader2 = new _TypeDSLLoader(unionOfundefinedtypeOrWorkflowStepTypeLoader, 2);
export const unionOfundefinedtypeOrGalaxyWorkflowLoader = new _UnionLoader([undefinedtype, GalaxyWorkflowLoader]);
export const uriunionOfundefinedtypeOrGalaxyWorkflowLoaderFalseFalseNone = new _URILoader(unionOfundefinedtypeOrGalaxyWorkflowLoader, false, false, undefined);
export const uriunionOfundefinedtypeOrstrtypeOrarrayOfstrtypeFalseFalse2 = new _URILoader(unionOfundefinedtypeOrstrtypeOrarrayOfstrtype, false, false, 2);
export const unionOfundefinedtypeOrbooltype = new _UnionLoader([undefinedtype, booltype]);
export const uristrtypeFalseTrueNone = new _URILoader(strtype, false, true, undefined);
export const arrayOfWorkflowInputParameterLoader = new _ArrayLoader([WorkflowInputParameterLoader]);
export const idmapinputsarrayOfWorkflowInputParameterLoader = new _IdMapLoader(arrayOfWorkflowInputParameterLoader, 'id', 'type');
export const arrayOfWorkflowOutputParameterLoader = new _ArrayLoader([WorkflowOutputParameterLoader]);
export const idmapoutputsarrayOfWorkflowOutputParameterLoader = new _IdMapLoader(arrayOfWorkflowOutputParameterLoader, 'id', 'type');
export const arrayOfWorkflowStepLoader = new _ArrayLoader([WorkflowStepLoader]);
export const unionOfarrayOfWorkflowStepLoader = new _UnionLoader([arrayOfWorkflowStepLoader]);
export const idmapstepsunionOfarrayOfWorkflowStepLoader = new _IdMapLoader(unionOfarrayOfWorkflowStepLoader, 'id', 'None');
export const unionOfundefinedtypeOrReportLoader = new _UnionLoader([undefinedtype, ReportLoader]);
export const unionOfarrayOfstrtypeOrundefinedtype = new _UnionLoader([arrayOfstrtype, undefinedtype]);
export const unionOfGalaxyWorkflowLoader = new _UnionLoader([GalaxyWorkflowLoader]);
export const arrayOfunionOfGalaxyWorkflowLoader = new _ArrayLoader([unionOfGalaxyWorkflowLoader]);
export const unionOfGalaxyWorkflowLoaderOrarrayOfunionOfGalaxyWorkflowLoader = new _UnionLoader([GalaxyWorkflowLoader, arrayOfunionOfGalaxyWorkflowLoader]);
