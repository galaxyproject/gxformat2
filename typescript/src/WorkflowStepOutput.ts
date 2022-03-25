
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
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput
 *
 * Associate an output parameter of the underlying process with a workflow
 * parameter.  The workflow parameter (given in the `id` field) be may be used
 * as a `source` to connect with input parameters of other workflow steps, or
 * with an output parameter of the process.
 * 
 * A unique identifier for this workflow output parameter.  This is
 * the identifier to use in the `source` field of `WorkflowStepInput`
 * to connect the output value to downstream parameters.
 * 
 */
export class WorkflowStepOutput extends Saveable implements Internal.WorkflowStepOutputProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * The unique identifier for this object.
   */
  id?: undefined | string
  add_tags?: undefined | Array<string>
  change_datatype?: undefined | string
  delete_intermediate_datasets?: undefined | boolean
  hide?: undefined | boolean
  remove_tags?: undefined | Array<string>
  rename?: undefined | string
  set_columns?: undefined | Array<string>


  constructor ({loadingOptions, extensionFields, id, add_tags, change_datatype, delete_intermediate_datasets, hide, remove_tags, rename, set_columns} : {loadingOptions?: LoadingOptions} & Internal.WorkflowStepOutputProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.id = id
    this.add_tags = add_tags
    this.change_datatype = change_datatype
    this.delete_intermediate_datasets = delete_intermediate_datasets
    this.hide = hide
    this.remove_tags = remove_tags
    this.rename = rename
    this.set_columns = set_columns
  }

  /**
   * Used to construct instances of {@link WorkflowStepOutput }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link WorkflowStepOutput }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let id
    if ('id' in _doc) {
      try {
        id = await loadField(_doc.id, LoaderInstances.uriunionOfundefinedtypeOrstrtypeTrueFalseNone,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `id` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    const originalidIsUndefined = (id === undefined)
    if (originalidIsUndefined ) {
      if (docRoot != null) {
        id = docRoot
      } else {
        id = "_" + uuidv4()
      }
    } else {
      baseuri = id as string
    }
            
    let add_tags
    if ('add_tags' in _doc) {
      try {
        add_tags = await loadField(_doc.add_tags, LoaderInstances.unionOfundefinedtypeOrarrayOfstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `add_tags` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let change_datatype
    if ('change_datatype' in _doc) {
      try {
        change_datatype = await loadField(_doc.change_datatype, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `change_datatype` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let delete_intermediate_datasets
    if ('delete_intermediate_datasets' in _doc) {
      try {
        delete_intermediate_datasets = await loadField(_doc.delete_intermediate_datasets, LoaderInstances.unionOfundefinedtypeOrbooltype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `delete_intermediate_datasets` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let hide
    if ('hide' in _doc) {
      try {
        hide = await loadField(_doc.hide, LoaderInstances.unionOfundefinedtypeOrbooltype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `hide` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let remove_tags
    if ('remove_tags' in _doc) {
      try {
        remove_tags = await loadField(_doc.remove_tags, LoaderInstances.unionOfundefinedtypeOrarrayOfstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `remove_tags` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let rename
    if ('rename' in _doc) {
      try {
        rename = await loadField(_doc.rename, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `rename` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let set_columns
    if ('set_columns' in _doc) {
      try {
        set_columns = await loadField(_doc.set_columns, LoaderInstances.unionOfundefinedtypeOrarrayOfstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `set_columns` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!WorkflowStepOutput.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`id\`,\`add_tags\`,\`change_datatype\`,\`delete_intermediate_datasets\`,\`hide\`,\`remove_tags\`,\`rename\`,\`set_columns\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'WorkflowStepOutput'", __errors)
    }

    const schema = new WorkflowStepOutput({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      id: id,
      add_tags: add_tags,
      change_datatype: change_datatype,
      delete_intermediate_datasets: delete_intermediate_datasets,
      hide: hide,
      remove_tags: remove_tags,
      rename: rename,
      set_columns: set_columns
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.id != null) {
      const u = saveRelativeUri(this.id, baseUrl, true,
                                relativeUris, undefined)
      if (u != null) {
        r.id = u
      }
    }
                
    if (this.add_tags != null) {
      r.add_tags = save(this.add_tags, false, this.id, relativeUris)
    }
                
    if (this.change_datatype != null) {
      r.change_datatype = save(this.change_datatype, false, this.id, relativeUris)
    }
                
    if (this.delete_intermediate_datasets != null) {
      r.delete_intermediate_datasets = save(this.delete_intermediate_datasets, false, this.id, relativeUris)
    }
                
    if (this.hide != null) {
      r.hide = save(this.hide, false, this.id, relativeUris)
    }
                
    if (this.remove_tags != null) {
      r.remove_tags = save(this.remove_tags, false, this.id, relativeUris)
    }
                
    if (this.rename != null) {
      r.rename = save(this.rename, false, this.id, relativeUris)
    }
                
    if (this.set_columns != null) {
      r.set_columns = save(this.set_columns, false, this.id, relativeUris)
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
            
  static attr: Set<string> = new Set(['id','add_tags','change_datatype','delete_intermediate_datasets','hide','remove_tags','rename','set_columns'])
}
