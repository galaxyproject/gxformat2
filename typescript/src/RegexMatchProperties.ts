
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#RegexMatch
 */
export interface RegexMatchProperties  {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * Check if a regular expression matches the value. A value is only valid if a match is found.
   */
  regex: string

  /**
   * Message to provide to user if validator did not succeed.
   */
  doc: string
}