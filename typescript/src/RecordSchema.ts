
import {
  Dictionary,
  expandUrl,
  loadField,
  LoaderInstances,
  LoadingOptions,
  Saveable,
  ValidationException,
  prefixUrl,
  save,
  saveRelativeUri
} from './util/Internal'
import { v4 as uuidv4 } from 'uuid'
import * as Internal from './util/Internal'


/**
 * Auto-generated class implementation for https://w3id.org/cwl/salad#RecordSchema
 */
export class RecordSchema extends Saveable implements Internal.RecordSchemaProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * Defines the fields of the record.
   */
  fields?: undefined | Array<Internal.RecordField>

  /**
   * Must be `record`
   */
  type: Internal.enum_d9cba076fca539106791a4f46d198c7fcfbdb779


  constructor ({loadingOptions, extensionFields, fields, type} : {loadingOptions?: LoadingOptions} & Internal.RecordSchemaProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.fields = fields
    this.type = type
  }

  /**
   * Used to construct instances of {@link RecordSchema }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link RecordSchema }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let fields
    if ('fields' in _doc) {
      try {
        fields = await loadField(_doc.fields, LoaderInstances.idmapfieldsunionOfundefinedtypeOrarrayOfRecordFieldLoader,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `fields` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let type
    try {
      type = await loadField(_doc.type, LoaderInstances.typedslenum_d9cba076fca539106791a4f46d198c7fcfbdb779Loader2,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `type` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!RecordSchema.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`fields\`,\`type\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'RecordSchema'", __errors)
    }

    const schema = new RecordSchema({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      fields: fields,
      type: type
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.fields != null) {
      r.fields = save(this.fields, false, baseUrl, relativeUris)
    }
                
    if (this.type != null) {
      r.type = save(this.type, false, baseUrl, relativeUris)
    }
                
    if (top) {
      if (this.loadingOptions.namespaces != null) {
        r.$namespaces = this.loadingOptions.namespaces
      }
      if (this.loadingOptions.schemas != null) {
        r.$schemas = this.loadingOptions.schemas
      }
    }
    return r
  }
            
  static attr: Set<string> = new Set(['fields','type'])
}
