
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
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository
 */
export class ToolShedRepository extends Saveable implements Internal.ToolShedRepositoryProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * The name of the tool shed repository this tool can be found in.
   * 
   */
  name: string

  /**
   * The revision of the tool shed repository this tool can be found in.
   * 
   */
  changeset_revision: string

  /**
   * The owner of the tool shed repository this tool can be found in.
   * 
   */
  owner: string

  /**
   * The URI of the tool shed containing the repository this tool can be found in - typically this should be toolshed.g2.bx.psu.edu.
   * 
   */
  tool_shed: string


  constructor ({loadingOptions, extensionFields, name, changeset_revision, owner, tool_shed} : {loadingOptions?: LoadingOptions} & Internal.ToolShedRepositoryProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.name = name
    this.changeset_revision = changeset_revision
    this.owner = owner
    this.tool_shed = tool_shed
  }

  /**
   * Used to construct instances of {@link ToolShedRepository }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link ToolShedRepository }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let name
    if ('name' in _doc) {
      try {
        name = await loadField(_doc.name, LoaderInstances.uristrtypeTrueFalseNone,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `name` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    const originalnameIsUndefined = (name === undefined)
    if (originalnameIsUndefined ) {
      if (docRoot != null) {
        name = docRoot
      } else {
        throw new ValidationException("Missing name")
      }
    } else {
      baseuri = name as string
    }
            
    let changeset_revision
    try {
      changeset_revision = await loadField(_doc.changeset_revision, LoaderInstances.strtype,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `changeset_revision` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let owner
    try {
      owner = await loadField(_doc.owner, LoaderInstances.strtype,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `owner` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let tool_shed
    try {
      tool_shed = await loadField(_doc.tool_shed, LoaderInstances.strtype,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `tool_shed` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!ToolShedRepository.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`changeset_revision\`,\`name\`,\`owner\`,\`tool_shed\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'ToolShedRepository'", __errors)
    }

    const schema = new ToolShedRepository({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      changeset_revision: changeset_revision,
      name: name,
      owner: owner,
      tool_shed: tool_shed
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.name != null) {
      const u = saveRelativeUri(this.name, baseUrl, true,
                                relativeUris, undefined)
      if (u != null) {
        r.name = u
      }
    }
                
    if (this.changeset_revision != null) {
      r.changeset_revision = save(this.changeset_revision, false, this.name, relativeUris)
    }
                
    if (this.owner != null) {
      r.owner = save(this.owner, false, this.name, relativeUris)
    }
                
    if (this.tool_shed != null) {
      r.tool_shed = save(this.tool_shed, false, this.name, relativeUris)
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
            
  static attr: Set<string> = new Set(['changeset_revision','name','owner','tool_shed'])
}
