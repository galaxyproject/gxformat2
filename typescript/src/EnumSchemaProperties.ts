
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://w3id.org/cwl/salad#EnumSchema
 *
 * Define an enumerated type.
 * 
 */
export interface EnumSchemaProperties  {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * Defines the set of valid symbols.
   */
  symbols: Array<string>

  /**
   * Must be `enum`
   */
  type: Internal.enum_d961d79c225752b9fadb617367615ab176b47d77
}