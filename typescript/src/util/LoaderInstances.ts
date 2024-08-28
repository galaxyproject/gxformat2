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
  _MapLoader,
  _TypeDSLLoader,
  _SecondaryDSLLoader,
  TypeGuards,
  Any,
  ArraySchema,
  ArraySchemaProperties,
  BaseDataParameter,
  BaseDataParameterProperties,
  BaseInputParameter,
  BaseInputParameterProperties,
  DocumentedProperties,
  EnumSchema,
  EnumSchemaProperties,
  GalaxyBooleanType,
  GalaxyDataCollectionType,
  GalaxyDataType,
  GalaxyFloatType,
  GalaxyIntegerType,
  GalaxyTextType,
  GalaxyType,
  GalaxyWorkflow,
  GalaxyWorkflowProperties,
  HasStepErrorsProperties,
  HasStepPositionProperties,
  HasUUIDProperties,
  IdentifiedProperties,
  InputParameterProperties,
  LabeledProperties,
  MinMax,
  MinMaxProperties,
  OutputParameterProperties,
  ParameterProperties,
  PrimitiveType,
  ProcessProperties,
  RecordField,
  RecordFieldProperties,
  RecordSchema,
  RecordSchemaProperties,
  ReferencesToolProperties,
  RegexMatch,
  RegexMatchProperties,
  Report,
  ReportProperties,
  SinkProperties,
  StepPosition,
  StepPositionProperties,
  TextValidators,
  TextValidatorsProperties,
  ToolShedRepository,
  ToolShedRepositoryProperties,
  WorkflowCollectionParameter,
  WorkflowCollectionParameterProperties,
  WorkflowDataParameter,
  WorkflowDataParameterProperties,
  WorkflowFloatParameter,
  WorkflowFloatParameterProperties,
  WorkflowIntegerParameter,
  WorkflowIntegerParameterProperties,
  WorkflowOutputParameter,
  WorkflowOutputParameterProperties,
  WorkflowStep,
  WorkflowStepInput,
  WorkflowStepInputProperties,
  WorkflowStepOutput,
  WorkflowStepOutputProperties,
  WorkflowStepProperties,
  WorkflowStepType,
  WorkflowTextParameter,
  WorkflowTextParameterProperties,
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
export const RecordFieldLoader = new _RecordLoader(RecordField.fromDoc, undefined, undefined);
export const RecordSchemaLoader = new _RecordLoader(RecordSchema.fromDoc, undefined, undefined);
export const EnumSchemaLoader = new _RecordLoader(EnumSchema.fromDoc, undefined, undefined);
export const ArraySchemaLoader = new _RecordLoader(ArraySchema.fromDoc, undefined, undefined);
export const StepPositionLoader = new _RecordLoader(StepPosition.fromDoc, undefined, undefined);
export const ToolShedRepositoryLoader = new _RecordLoader(ToolShedRepository.fromDoc, undefined, undefined);
export const GalaxyTypeLoader = new _EnumLoader((Object.keys(GalaxyType) as Array<keyof typeof GalaxyType>).map(key => GalaxyType[key]));
export const GalaxyTextTypeLoader = new _EnumLoader((Object.keys(GalaxyTextType) as Array<keyof typeof GalaxyTextType>).map(key => GalaxyTextType[key]));
export const GalaxyIntegerTypeLoader = new _EnumLoader((Object.keys(GalaxyIntegerType) as Array<keyof typeof GalaxyIntegerType>).map(key => GalaxyIntegerType[key]));
export const GalaxyFloatTypeLoader = new _EnumLoader((Object.keys(GalaxyFloatType) as Array<keyof typeof GalaxyFloatType>).map(key => GalaxyFloatType[key]));
export const GalaxyBooleanTypeLoader = new _EnumLoader((Object.keys(GalaxyBooleanType) as Array<keyof typeof GalaxyBooleanType>).map(key => GalaxyBooleanType[key]));
export const GalaxyDataTypeLoader = new _EnumLoader((Object.keys(GalaxyDataType) as Array<keyof typeof GalaxyDataType>).map(key => GalaxyDataType[key]));
export const GalaxyDataCollectionTypeLoader = new _EnumLoader((Object.keys(GalaxyDataCollectionType) as Array<keyof typeof GalaxyDataCollectionType>).map(key => GalaxyDataCollectionType[key]));
export const WorkflowStepTypeLoader = new _EnumLoader((Object.keys(WorkflowStepType) as Array<keyof typeof WorkflowStepType>).map(key => WorkflowStepType[key]));
export const BaseInputParameterLoader = new _RecordLoader(BaseInputParameter.fromDoc, undefined, undefined);
export const BaseDataParameterLoader = new _RecordLoader(BaseDataParameter.fromDoc, undefined, undefined);
export const WorkflowDataParameterLoader = new _RecordLoader(WorkflowDataParameter.fromDoc, undefined, undefined);
export const WorkflowCollectionParameterLoader = new _RecordLoader(WorkflowCollectionParameter.fromDoc, undefined, undefined);
export const MinMaxLoader = new _RecordLoader(MinMax.fromDoc, undefined, undefined);
export const WorkflowIntegerParameterLoader = new _RecordLoader(WorkflowIntegerParameter.fromDoc, undefined, undefined);
export const WorkflowFloatParameterLoader = new _RecordLoader(WorkflowFloatParameter.fromDoc, undefined, undefined);
export const TextValidatorsLoader = new _RecordLoader(TextValidators.fromDoc, undefined, undefined);
export const RegexMatchLoader = new _RecordLoader(RegexMatch.fromDoc, undefined, undefined);
export const WorkflowTextParameterLoader = new _RecordLoader(WorkflowTextParameter.fromDoc, undefined, undefined);
export const WorkflowInputParameterLoader = new _UnionLoader([]);
export const WorkflowOutputParameterLoader = new _RecordLoader(WorkflowOutputParameter.fromDoc, undefined, undefined);
export const WorkflowStepLoader = new _RecordLoader(WorkflowStep.fromDoc, undefined, undefined);
export const WorkflowStepInputLoader = new _RecordLoader(WorkflowStepInput.fromDoc, undefined, undefined);
export const ReportLoader = new _RecordLoader(Report.fromDoc, undefined, undefined);
export const WorkflowStepOutputLoader = new _RecordLoader(WorkflowStepOutput.fromDoc, undefined, undefined);
export const GalaxyWorkflowLoader = new _RecordLoader(GalaxyWorkflow.fromDoc, undefined, undefined);
export const arrayOfstrtype = new _ArrayLoader([strtype]);
export const unionOfundefinedtypeOrstrtypeOrarrayOfstrtype = new _UnionLoader([undefinedtype, strtype, arrayOfstrtype]);
export const uristrtypeTrueFalseNoneNone = new _URILoader(strtype, true, false, undefined, undefined);
export const unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype = new _UnionLoader([PrimitiveTypeLoader, RecordSchemaLoader, EnumSchemaLoader, ArraySchemaLoader, strtype]);
export const arrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype = new _ArrayLoader([unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype]);
export const unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype = new _UnionLoader([PrimitiveTypeLoader, RecordSchemaLoader, EnumSchemaLoader, ArraySchemaLoader, strtype, arrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype]);
export const typedslunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype2 = new _TypeDSLLoader(unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype, 2);
export const arrayOfRecordFieldLoader = new _ArrayLoader([RecordFieldLoader]);
export const unionOfundefinedtypeOrarrayOfRecordFieldLoader = new _UnionLoader([undefinedtype, arrayOfRecordFieldLoader]);
export const idmapfieldsunionOfundefinedtypeOrarrayOfRecordFieldLoader = new _IdMapLoader(unionOfundefinedtypeOrarrayOfRecordFieldLoader, 'name', 'type');
export const enum_d9cba076fca539106791a4f46d198c7fcfbdb779Loader = new _EnumLoader((Object.keys(enum_d9cba076fca539106791a4f46d198c7fcfbdb779) as Array<keyof typeof enum_d9cba076fca539106791a4f46d198c7fcfbdb779>).map(key => enum_d9cba076fca539106791a4f46d198c7fcfbdb779[key]));
export const typedslenum_d9cba076fca539106791a4f46d198c7fcfbdb779Loader2 = new _TypeDSLLoader(enum_d9cba076fca539106791a4f46d198c7fcfbdb779Loader, 2);
export const uriarrayOfstrtypeTrueFalseNoneNone = new _URILoader(arrayOfstrtype, true, false, undefined, undefined);
export const enum_d961d79c225752b9fadb617367615ab176b47d77Loader = new _EnumLoader((Object.keys(enum_d961d79c225752b9fadb617367615ab176b47d77) as Array<keyof typeof enum_d961d79c225752b9fadb617367615ab176b47d77>).map(key => enum_d961d79c225752b9fadb617367615ab176b47d77[key]));
export const typedslenum_d961d79c225752b9fadb617367615ab176b47d77Loader2 = new _TypeDSLLoader(enum_d961d79c225752b9fadb617367615ab176b47d77Loader, 2);
export const uriunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeFalseTrue2None = new _URILoader(unionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtypeOrarrayOfunionOfPrimitiveTypeLoaderOrRecordSchemaLoaderOrEnumSchemaLoaderOrArraySchemaLoaderOrstrtype, false, true, 2, undefined);
export const enum_d062602be0b4b8fd33e69e29a841317b6ab665bcLoader = new _EnumLoader((Object.keys(enum_d062602be0b4b8fd33e69e29a841317b6ab665bc) as Array<keyof typeof enum_d062602be0b4b8fd33e69e29a841317b6ab665bc>).map(key => enum_d062602be0b4b8fd33e69e29a841317b6ab665bc[key]));
export const typedslenum_d062602be0b4b8fd33e69e29a841317b6ab665bcLoader2 = new _TypeDSLLoader(enum_d062602be0b4b8fd33e69e29a841317b6ab665bcLoader, 2);
export const unionOfundefinedtypeOrstrtype = new _UnionLoader([undefinedtype, strtype]);
export const uriunionOfundefinedtypeOrstrtypeTrueFalseNoneNone = new _URILoader(unionOfundefinedtypeOrstrtype, true, false, undefined, undefined);
export const unionOfundefinedtypeOranyType = new _UnionLoader([undefinedtype, anyType]);
export const unionOfBaseInputParameterLoader = new _UnionLoader([BaseInputParameterLoader]);
export const arrayOfunionOfBaseInputParameterLoader = new _ArrayLoader([unionOfBaseInputParameterLoader]);
export const idmapinputsarrayOfunionOfBaseInputParameterLoader = new _IdMapLoader(arrayOfunionOfBaseInputParameterLoader, 'id', 'type');
export const unionOfWorkflowOutputParameterLoader = new _UnionLoader([WorkflowOutputParameterLoader]);
export const arrayOfunionOfWorkflowOutputParameterLoader = new _ArrayLoader([unionOfWorkflowOutputParameterLoader]);
export const idmapoutputsarrayOfunionOfWorkflowOutputParameterLoader = new _IdMapLoader(arrayOfunionOfWorkflowOutputParameterLoader, 'id', 'type');
export const unionOfundefinedtypeOrStepPositionLoader = new _UnionLoader([undefinedtype, StepPositionLoader]);
export const unionOffloattypeOrinttype = new _UnionLoader([floattype, inttype]);
export const unionOfundefinedtypeOrToolShedRepositoryLoader = new _UnionLoader([undefinedtype, ToolShedRepositoryLoader]);
export const unionOfbooltypeOrundefinedtype = new _UnionLoader([booltype, undefinedtype]);
export const unionOfundefinedtypeOrarrayOfstrtype = new _UnionLoader([undefinedtype, arrayOfstrtype]);
export const unionOfGalaxyDataTypeLoaderOrundefinedtype = new _UnionLoader([GalaxyDataTypeLoader, undefinedtype]);
export const typedslunionOfGalaxyDataTypeLoaderOrundefinedtype2 = new _TypeDSLLoader(unionOfGalaxyDataTypeLoaderOrundefinedtype, 2);
export const typedslGalaxyDataCollectionTypeLoader2 = new _TypeDSLLoader(GalaxyDataCollectionTypeLoader, 2);
export const unionOfinttypeOrfloattypeOrundefinedtype = new _UnionLoader([inttype, floattype, undefinedtype]);
export const unionOfWorkflowIntegerParameterLoader = new _UnionLoader([WorkflowIntegerParameterLoader]);
export const arrayOfunionOfWorkflowIntegerParameterLoader = new _ArrayLoader([unionOfWorkflowIntegerParameterLoader]);
export const unionOfGalaxyIntegerTypeLoaderOrarrayOfunionOfWorkflowIntegerParameterLoader = new _UnionLoader([GalaxyIntegerTypeLoader, arrayOfunionOfWorkflowIntegerParameterLoader]);
export const typedslunionOfGalaxyIntegerTypeLoaderOrarrayOfunionOfWorkflowIntegerParameterLoader2 = new _TypeDSLLoader(unionOfGalaxyIntegerTypeLoaderOrarrayOfunionOfWorkflowIntegerParameterLoader, 2);
export const unionOfWorkflowFloatParameterLoader = new _UnionLoader([WorkflowFloatParameterLoader]);
export const arrayOfunionOfWorkflowFloatParameterLoader = new _ArrayLoader([unionOfWorkflowFloatParameterLoader]);
export const unionOfGalaxyFloatTypeLoaderOrarrayOfunionOfWorkflowFloatParameterLoader = new _UnionLoader([GalaxyFloatTypeLoader, arrayOfunionOfWorkflowFloatParameterLoader]);
export const typedslunionOfGalaxyFloatTypeLoaderOrarrayOfunionOfWorkflowFloatParameterLoader2 = new _TypeDSLLoader(unionOfGalaxyFloatTypeLoaderOrarrayOfunionOfWorkflowFloatParameterLoader, 2);
export const unionOfRegexMatchLoader = new _UnionLoader([RegexMatchLoader]);
export const unionOfstrtype = new _UnionLoader([strtype]);
export const unionOfWorkflowTextParameterLoader = new _UnionLoader([WorkflowTextParameterLoader]);
export const arrayOfunionOfWorkflowTextParameterLoader = new _ArrayLoader([unionOfWorkflowTextParameterLoader]);
export const unionOfGalaxyTextTypeLoaderOrarrayOfunionOfWorkflowTextParameterLoader = new _UnionLoader([GalaxyTextTypeLoader, arrayOfunionOfWorkflowTextParameterLoader]);
export const typedslunionOfGalaxyTextTypeLoaderOrarrayOfunionOfWorkflowTextParameterLoader2 = new _TypeDSLLoader(unionOfGalaxyTextTypeLoaderOrarrayOfunionOfWorkflowTextParameterLoader, 2);
export const arrayOfTextValidatorsLoader = new _ArrayLoader([TextValidatorsLoader]);
export const unionOfundefinedtypeOrarrayOfTextValidatorsLoader = new _UnionLoader([undefinedtype, arrayOfTextValidatorsLoader]);
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
export const uriunionOfundefinedtypeOrGalaxyWorkflowLoaderFalseFalseNoneNone = new _URILoader(unionOfundefinedtypeOrGalaxyWorkflowLoader, false, false, undefined, undefined);
export const uriunionOfundefinedtypeOrstrtypeOrarrayOfstrtypeFalseFalse2None = new _URILoader(unionOfundefinedtypeOrstrtypeOrarrayOfstrtype, false, false, 2, undefined);
export const unionOfundefinedtypeOrbooltype = new _UnionLoader([undefinedtype, booltype]);
export const uristrtypeFalseTrueNoneNone = new _URILoader(strtype, false, true, undefined, undefined);
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

WorkflowInputParameterLoader.addLoaders([WorkflowTextParameterLoader, WorkflowFloatParameterLoader, WorkflowIntegerParameterLoader, WorkflowDataParameterLoader, WorkflowCollectionParameterLoader]);
